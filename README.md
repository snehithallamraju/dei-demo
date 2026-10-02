# One Question, Many Roles — Demo Kit

A 20-minute live relay for the guest lecture. One business question travels through eight roles on the career map, all running offline on a MacBook.

**The business:** a fictional food-delivery company in Agra.
**The question:** *"Why are repeat orders dropping?"*
**The answer (planted in the data):** deliveries in Sikandra and Shahganj got slower every month, and customers who get a late delivery rarely come back.

---

## 1. Setup (do this at the hotel, with Wi-Fi)

```bash
brew install duckdb                    # the SQL engine
python3 -m pip install duckdb pandas   # for ask.py
cd demo-kit
./build_all.sh                      # builds everything once, as a test and a backup
```

In **LM Studio**: download Gemma 4 E4B, load it, then open the **Developer** tab and switch the local server **on** (it runs at `localhost:1234`). `ask.py` finds your Gemma model automatically.

Then **turn Wi-Fi off and rehearse the whole relay once.** Everything below runs offline.

Terminal tips: raise the font size to 20pt or more, use a light theme on a projector, and keep this README open on your phone.

The dataset is already in `data/orders_raw.csv`. `generate_data.py` recreates it identically if you ever need to.

---

## 2. The relay

Start DuckDB once and leave it open for steps 1–5:

```bash
duckdb demo.duckdb
.mode box
```

### Role card 1 — Business Analyst / Product Manager (1 min)
No code. Write the question on the board: *"Why are repeat orders dropping?"*
Say: a vague question like "use AI on our data" goes nowhere. A sharp question gets an answer.

### Role card 2 — Data Engineer (2 min)
```
.read sql/00_setup_raw.sql
.read sql/01_look_at_the_mess.sql
```
**What they'll see:** about 3,400 rows. Three date formats, rupee signs inside numbers, "27 min" instead of 27, blank order IDs, and **24 spellings for 8 areas**.
Say: this is what real data looks like on day one. Someone has to make it usable.

### Role card 3 — Data Governance / MDM (3 min) ⭐ the aha moment
First ask the room: **"Which restaurant earns the most?"**
```
.read sql/02_mdm_before.sql
```
**What they'll see:** Agra Tandoor House is #1 at about ₹1.8 lakh. Let the room agree. Then read slowly down the list: *Mama's Kitchen… MAMAS KITCHEN… Mama's Kitchen - Agra… mamas kitchen.*
```
.read sql/03_mdm_master.sql
.read sql/04_mdm_after.sql
```
**What they'll see:** Mama's Kitchen jumps to #1 at about ₹2.8 lakh, 50% ahead of the "winner."
Say: every dashboard, every bonus, every AI answer built on the raw names would have been confidently wrong. Master data management is making sure one real-world thing has one record.

### Role card 4 — Analytics Engineer (2 min)
```
.read sql/05_analytics_engineer_model.sql
```
**What they'll see:** a clean table, and four data tests that all return **0**.
Say: the Data Engineer fixed it once. The Analytics Engineer makes sure it stays fixed every single day, with tests that stop the pipeline if something breaks.

### Role card 5 — Data Analyst (2 min)
```
.read sql/06_analyst_insights.sql
```
**What they'll see:**

| Finding | Number |
|---|---|
| Reorder rate, January → May | 79% → 64% |
| Reorder rate after an on-time delivery | about 80% |
| Reorder rate after a late delivery (over 45 min) | about 30% |
| Late deliveries in Sikandra and Shahganj | nearly 1 in 2 |
| Late deliveries in every other area | about 2% |

Say: the answer isn't the food, the price, or the app. It's delivery speed in two areas. That's an insight a manager can act on tomorrow.

Type `.quit` to leave DuckDB.

### Role card 6 — AI / LLM Engineer (3 min)
**Turn Wi-Fi off in front of the room.** (LM Studio's server must be on, with Gemma loaded.)
```bash
python3 ask.py "Which area had the most late deliveries?"
```
Gemma writes the SQL, DuckDB runs it, results appear. Say: no internet, no cloud, no subscription.

Rehearsed questions that should work (test each 5–10 times at the hotel and keep the ones that never fail):
- "Which area had the most late deliveries?"
- "Compare the reorder rate for late and on-time deliveries."
- "Which restaurant earned the most revenue?"
- "What is the average delivery time by month for Sikandra?"

If the model writes bad SQL, the script says so. Use it: *"This is why companies still need people who can read SQL."*

### Role card 7 — AI FinOps (2 min)
The same `ask.py` output ends with the token count. Then run it with a real cloud price:
```bash
python3 ask.py "Which area had the most late deliveries?" --price-in <X> --price-out <Y> --users 10000 --usd-inr <rate>
```
`<X>` and `<Y>` are USD per million input/output tokens. **Look up a current price for a real cloud model the week before** and put the source on your slide. The script shows cost per question, per day, and per year for 10,000 employees asking 5 questions a day.
Say: every AI answer has a bill. Someone has to decide whether it's worth it.

### Role card 8 — AI Product Manager (2 min)
No code. Ask the room to vote: *"Is this AI assistant worth building, or would a simple dashboard do the job?"*
There's no right answer. Deciding that is the job.

---

## 3. Bonus: the vision demo (Data Engineer, 2 min)

A photo of a paper bill becomes a data table, offline, in LM Studio's chat window:

1. Open a new chat in LM Studio with Gemma 4 E4B loaded.
2. Drag `images/sample_bill.jpg` into the message box.
3. Type: *"Extract every line item from this bill as a table with columns item, quantity, amount. Then give the total."*

The chat window is friendlier on a projector than the terminal. A real bill photographed on the day is more impressive, but test with a similar photo first.

---

## 4. Backup plan

- If a live step breaks, `./build_all.sh` rebuilds everything in seconds.
- Record a 60-second screen capture of steps 3 and 6 at the hotel. If the projector or laptop misbehaves, play the video.
- Load Gemma in LM Studio before the session and run one warm-up question, so it isn't loading into memory in front of the room.
- If `ask.py` says it can't reach LM Studio, the local server is off: Developer tab → switch it on.

## Files

| File | Purpose |
|---|---|
| `data/orders_raw.csv` | The messy dataset |
| `sql/00`–`06` | One file per role, in relay order |
| `ask.py` | Offline question → SQL → answer via LM Studio, plus token cost (`--backend ollama` also works) |
| `images/sample_bill.jpg` | For the vision demo |
| `role_cards.html` | Open in a browser and print; hand to volunteers |
| `build_all.sh` | Builds everything in one go |
| `generate_data.py` | Recreates the dataset |
