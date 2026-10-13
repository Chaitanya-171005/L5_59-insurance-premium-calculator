# Lab 5: Static Code Analysis — Insurance Premium Calculator

**Your file:** `premium_calculator.py`

Follow the lab handout for the full instructions.

## About the program

An insurance premium calculator. It quotes health, motor and life premiums, works out an applicant's age, saves quotes to a log, imports policies from partner XML, downloads rate tables, extracts customer claim archives, splits premiums into instalments, and computes renewal dates.

The code works, but only just. It has quality, style and security problems of the kind Pylint, Flake8 and Bandit are built to find.

## What to do

1. **Run it first** and read the output carefully:
   ```bash
   python premium_calculator.py
   ```
   Check whether every number and date it prints makes sense, then try changing the inputs in `main()` to see what happens. Not every problem in this file is something a tool will flag, so pay attention to output that looks wrong.

2. **Install the tools:**
   ```bash
   python -m pip install pylint bandit flake8 defusedxml
   ```

3. **Run the analysis** and save the reports:
   ```bash
   python -m pylint premium_calculator.py > pylint_report.txt
   python -m bandit -r premium_calculator.py > bandit_report.txt
   python -m flake8 premium_calculator.py > flake8_report.txt
   ```

4. **Document the issues** in `issues.md` using this table (at least 4 rows, high and medium severity first):

   | Issue | Type | Line(s) | Description | Fix Approach |
   |-------|------|---------|-------------|--------------|
   | ... | ... | ... | ... | ... |

5. **Fix the code.** Fix at least 4 of the issues you documented, then rerun all three tools to confirm they are gone. Repeat until you are satisfied. The program should still do its job when you are done.

6. **Reflect.** Answer the four reflection questions from the handout in `reflection.md`.

## Deliverables

1. `premium_calculator.py`: your cleaned version, with at least 4 issues fixed.
2. `issues.md`: the completed issue table.
3. `reflection.md`: your answers to the reflection questions.

**Target:** aim for a Pylint score above 9.5 on your final file. A perfect 10.00/10 is very good.

Be ready to explain the bugs you found and how you fixed them. You may be called on to present.
