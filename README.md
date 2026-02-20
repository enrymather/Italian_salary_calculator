# RAL → Reddito Netto Calculator

**Version:** 1.0.0

This Streamlit app allows users to calculate their **net annual and monthly salary** (reddito netto) in Italy based on the gross RAL (Retribuzione Annua Lorda) and additional parameters such as region, company size, and fiscal benefits.

---

## Features

- Input gross salary (RAL) and view net annual/monthly salary.
- Compute IRPEF (Italian personal income tax) in detail, including regional and municipal tax rates.
- Include fiscal benefits (e.g., "rientro dei cervelli").
- Visualize salary composition with:
  - Interactive **pie chart**
  - **Stacked bar chart** showing salary components across RAL ranges
- Toggle monthly values in the pie chart.
- Modern, responsive UI with an adjustable slider for instant recalculation.

---

## Technical Notes / Assumptions

- **IRPEF Brackets** (2026 Italian rates assumed):

  + 23% up to €28,000

  + 33% from €28,001 to €50,000

  + 43% above €50,000

- **Employee contribution rates**:

  + 9.49% for companies ≥ 15 employees

  + 9.19% for companies < 15 employees

- **Regional and municipal tax rates**:

  + Default: 2% regional, 0.8% municipal

  + Can be customized per user input

- **Main tax credit -> _detrazione lavoro dipendente_** (dependent on taxable income):

  + Up to €15,000 -> €1,955

  + €15,001–28,000 -> linear reduction

  + €28,001–50,000 -> further reduction

  + €50,000 -> €0

- **Further tax credits -> _ulteriori detrazioni_** applied for certain RAL ranges, e.g. €1,000 for €20,000 to €32,000.

- **_Bonus cuneo fiscale_** included for RAL ≤ €20,000, following simplified rates.

- **Fiscal benefit (e.g. “rientro dei cervelli”)**: user can specify percentage of taxable income exempt from IRPEF.

**Note**: All computations are simplified approximations for demo purposes. Real-world payroll calculations may involve additional factors like pension schemes, company-specific benefits, or deductions.

---

## Usage

1. Clone the repository:

```bash
git clone https://github.com/<yourusername>/Italian_salary_calculator.git
cd Italian_salary_calculator
```

2. Install dependencies:

```bash
pip install -r salary_app_requirements.txt
```

3. Run the app locally:

```bash
streamlit run Italian_salary_app.py
```

4. Interact with the app in your browser.

---

## Contributing

Feel free to open issues or submit pull requests. Suggestions to improve calculations, UI, or documentation are welcome.

---

## Author

Enrico Di Muzio
GitHub: https://github.com/enrymather

Email: <enrico.dimuzio@gmail.com>

