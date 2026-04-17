import os
import time
import psycopg2
from psycopg2 import pool
from groq import Groq
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import redis

# Load environment variables
load_dotenv()

app = FastAPI(title="Pharma Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PharmaChatbot:
    def __init__(self):
        self.db_url = os.environ.get("DATABASE_URL")
        self.groq_api_key = os.environ.get("GROQ_API_KEY")

        if not self.db_url or not self.groq_api_key:
            print("WARNING: Missing DATABASE_URL or GROQ_API_KEY")

        self.client = Groq(api_key=self.groq_api_key) if self.groq_api_key else None

        # ✅ Redis Setup with validation
        self.redis_host = os.environ.get("REDIS_HOST", "localhost")
        self.redis_port = int(os.environ.get("REDIS_PORT", 6379))
        try:
            self.redis = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                decode_responses=True
            )
            self.redis.ping()
            print(f"✅ Redis connected at {self.redis_host}:{self.redis_port}")
        except Exception as e:
            print(f"⚠️ Redis unavailable: {e}")
            self.redis = None

        # ✅ DB Connection Pool
        try:
            self.db_pool = pool.SimpleConnectionPool(1, 10, self.db_url)
            print("✅ PostgreSQL connection pool created")
        except Exception as e:
            print(f"⚠️ DB Pool failed: {e}")
            self.db_pool = None

        self.schema_definition = """
        Table: pharma_sales
        Columns:
        - id (UUID)
        - organization_id (UUID)
        - product_id (UUID)
        - doctor_id (UUID)
        - product_name (TEXT)
        - composition (TEXT)
        - sales_price (NUMERIC)
        - purchase_price (NUMERIC)
        - combo_type (TEXT)
        - total_strips (INT)
        - total_tablets (INT)
        - scheme (TEXT)
        - gift_sample (TEXT)
        - created_at (TIMESTAMP)
        """

    # ✅ DB Retry Mechanism
    def _get_db_connection(self):
        if not self.db_pool:
            raise Exception("Database pool not initialized")

        for _ in range(5):
            try:
                return self.db_pool.getconn()
            except Exception as e:
                print(f"DB retry... {e}")
                time.sleep(2)

        raise Exception("Database unavailable after retries")

    def _release_connection(self, conn):
        if self.db_pool:
            self.db_pool.putconn(conn)

    # ✅ AI Generation (Greeting or SQL)
    def _get_sql_query(self, user_query):
        if not self.client:
            raise ValueError("GROQ_API_KEY is not configured.")

        prompt = f"""
        You are a strict PostgreSQL SQL generator for a pharmaceutical sales database.

        YOUR ONLY JOB is to convert user questions into valid SQL queries using the given schema.

        SCHEMA:
        Table: pharma_sales
        Columns: product_name, composition, sales_price, purchase_price, combo_type, scheme, gift_sample, total_strips, total_tablets

        STEP 1: GREETING HANDLING
        If the user input is a greeting such as:
        "hi", "hello", "hey", "how are you"
        → Return EXACTLY this: Hello! 👋 I can help you with pharma sales data. What would you like to know?
        DO NOT generate SQL for greetings.

        STEP 2: STRICT RULE (MANDATORY)
        For ALL data-related questions:
        - You MUST generate a SQL query.
        - You MUST NOT answer using general knowledge.
        - You MUST NOT hallucinate.
        - You MUST ONLY use the pharma_sales table.

        STEP 3: BUSINESS LOGIC MAPPING (MANDATORY)
        Interpret user terms as follows:
        - "offer", "offers", "free", "deal" → combo_type OR scheme
        - "gift" → gift_sample
        - "price" → sales_price
        - "cost" → purchase_price
        - "discount" → (sales_price - purchase_price)
        - "no offer" → combo_type IS NULL AND scheme IS NULL

        STEP 4: FILTER RULES (STRICT ENFORCEMENT)
        If user asks about "offer", "discount", "free", or "deal":
        You MUST include this condition: WHERE combo_type IS NOT NULL OR scheme IS NOT NULL

        STEP 5: SQL GENERATION RULES
        - Only SELECT queries allowed. Use valid PostgreSQL syntax.
        - Always use LIMIT 10 unless specified. If user says "all", DO NOT use LIMIT.
        - "highest", "maximum", "top" → ORDER BY [column] DESC LIMIT 1
        - "lowest", "minimum" → ORDER BY [column] ASC LIMIT 1
        - "average" → AVG(), "total" → SUM(), "count" → COUNT(*)

        STEP 6: SPECIAL CASES (IMPORTANT)
        For "available discount":
        SELECT product_name, (sales_price - purchase_price) AS discount FROM pharma_sales ORDER BY discount DESC LIMIT 10;
        
        For "products with offers":
        SELECT product_name FROM pharma_sales WHERE combo_type IS NOT NULL OR scheme IS NOT NULL LIMIT 10;

        STEP 7: OFFER DETAILS (MANDATORY)
        If the user asks for "offer details", "what is the offer", or "show offers":
        - You MUST SELECT: product_name, combo_type, scheme
        - You MUST include: WHERE combo_type IS NOT NULL OR scheme IS NOT NULL

        STEP 8: VALUE LOGIC
        Retrieve raw data. Do not format or combine values in SQL.

        OUTPUT RULES:
        - If greeting → return only text response.
        - Otherwise → return ONLY SQL query. No markdown. No extra text.

        USER INPUT: {user_query}
        """

        completion = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )

        response = completion.choices[0].message.content.strip()

        # Remove markdown if exists
        if response.startswith("```"):
            response = response.replace("```sql", "").replace("```", "").strip()

        print(f"DEBUG LLM Response: {response}")
        return response

    # ✅ SQL Validation
    def _validate_sql(self, sql, user_query):
        sql_upper = sql.upper().strip()
        if not sql_upper.startswith("SELECT"):
            return False, "Error: Only SELECT queries are permitted."

        # Mandatory columns for offer queries
        offer_keywords = ["offer", "discount", "free", "deal", "gift"]
        if any(kw in user_query.lower() for kw in offer_keywords):
            required = ["product_name", "combo_type", "scheme"]
            # Only enforce if not an aggregation query
            if not any(agg in sql_upper for agg in ["COUNT", "SUM", "AVG", "MAX", "MIN"]):
                for col in required:
                    if col not in sql.lower():
                        return False, f"Error: Offer query missing mandatory column '{col}'"
        
        return True, None

    # ✅ SQL Execution with Safety
    def _execute_sql(self, sql, query):
        valid, error = self._validate_sql(sql, query)
        if not valid:
            return error

        try:
            conn = self._get_db_connection()
            cur = conn.cursor()
            cur.execute(sql)
            results = cur.fetchall()
            colnames = [desc[0] for desc in cur.description]
            cur.close()
            self._release_connection(conn)
            return {"columns": colnames, "data": results}
        except Exception as e:
            return f"Database Error: {str(e)}"

    # ✅ Deterministic Response Formatting
    def _format_response(self, query, results):
        if isinstance(results, str):
            return results
        if not results["data"]:
            return "No results found."

        data = results["data"]
        cols = results["columns"]
        formatted_rows = []

        for row in data:
            row_dict = dict(zip(cols, row))
            name = row_dict.get("product_name")
            combo = row_dict.get("combo_type")
            scheme = row_dict.get("scheme")

            # Check if this looks like an offer result
            if name and (combo or scheme):
                # Handle null/None values safely
                combo_str = str(combo) if combo else None
                scheme_str = str(scheme) if scheme else None

                if combo_str and scheme_str:
                    val = f"{combo_str} ({scheme_str})"
                else:
                    val = combo_str or scheme_str

                formatted_rows.append(f"• {name} → {val}")
            else:
                # Fallback for simple single-column or generic data
                line = " | ".join(str(v) for v in row if v is not None)
                formatted_rows.append(f"• {line}")

        return "\n".join(formatted_rows)

    # ✅ Main Processing with Redis
    def process_query(self, query):
        # 1. Cache check
        if self.redis:
            try:
                cached = self.redis.get(query)
                if cached:
                    print("⚡ Cache hit")
                    return cached
            except Exception:
                pass

        print("🔄 Cache miss")

        # 2. Get LLM response (Greeting or SQL)
        llm_response = self._get_sql_query(query)

        # 3. Handle Greetings (if response is not a SQL query)
        if not llm_response.strip().upper().startswith("SELECT"):
            # Store greeting in cache too for efficiency
            if self.redis:
                try:
                    self.redis.setex(query, 3600, llm_response)
                except Exception:
                    pass
            return llm_response

        # 4. Execute SQL
        result = self._execute_sql(llm_response, query)
        
        # 5. Format response
        response = self._format_response(query, result)

        # 6. Cache store
        if self.redis:
            try:
                self.redis.setex(query, 3600, response)
            except Exception:
                pass

        return response


# API Models
class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    answer: str


bot = PharmaChatbot()


@app.get("/")
def root():
    return {"status": "Running"}


@app.post("/ask", response_model=ChatResponse)
def ask(request: ChatRequest):
    try:
        answer = bot.process_query(request.query)
        return ChatResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)