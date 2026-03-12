# Finance Rankings

A research-oriented project that measures institutional research output in finance using a fractional authorship methodology.

**Live site:**
https://financerankings.netlify.app

---

## Motivation

Most existing finance department rankings rely on simple publication counts or weighted journal lists.

These approaches often fail to account for multi-author papers and differences in collaboration structure.

This project explores a **fractional authorship approach** to measuring institutional research output in finance.

The goal is to build a **transparent and reproducible ranking system** that better reflects how research contributions are actually distributed.

---

## Who is this for?

This project is intended for several audiences interested in understanding research output in finance:

**Researchers and Academics**

* Explore institutional research productivity using transparent methodology.
* Compare research output across universities and departments.

**Prospective PhD Students**

* Gain insights into which institutions are producing influential finance research.
* Use rankings as an additional reference when evaluating PhD programs.

**Policy Analysts and Administrators**

* Understand patterns of research productivity across institutions.
* Evaluate institutional performance using reproducible metrics.

**Students and Independent Researchers**

* Learn how research rankings can be constructed using open data and transparent methods.

---

## Methodology

The ranking system uses **fractional authorship weighting**.

For each paper:

* Credit is divided among co-authors
* Each author's institution receives the corresponding fractional credit
* Institutional output is computed by aggregating these fractional contributions

Example:

Paper with 4 authors → each author receives **0.25 credit**

If two authors belong to the same institution:

Institution credit = **0.5**

This approach avoids overcounting collaborative work.

---

## Project Structure

```
finance-rankings
│
├── backend/                 # Data processing and ranking computation
├── frontend/                # Web interface
├── financerankings-site/    # Website deployment files
└── README.md
```

---

## Website

The rankings are published here:

https://financerankings.netlify.app

The website is automatically deployed using **Netlify** with continuous deployment from GitHub.

---

## Deployment Workflow

```
Local development
        ↓
git push
        ↓
GitHub repository
        ↓
Netlify automatic build
        ↓
Live website update
```

---

## Future Improvements

* Expand journal coverage
* Improve author–institution disambiguation
* Add historical rankings
* Provide downloadable datasets
* Add methodology documentation

---

## Transparency

The goal of this project is to maintain **transparent ranking methodology**.

All code used to compute rankings is available in this repository.

---

## License

Open source for research and educational purposes.
