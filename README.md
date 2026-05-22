# LoLdle Solver

A simple Flask web app that helps solve [LoLdle](https://loldle.net/classic) champion guesses. Enter a champion guess and select the feedback colors for each category. The app filters the possible champions and keeps a guess history until you reset.

> **Note:** This app is hosted on Render. If the server has spun down due to inactivity, the first load may take up to a minute while it spins back up.
>
> **Last updated:** 22 May 2026
>
> Champion data may become outdated over time. Riot may add new champions, update champion details, add or retcon lore, or otherwise change information that affects LoLdle answers.

## Features

- Searchable champion input
- Feedback options for Gender, Position, Species, Resource, Range, Region, and Year
- Candidate list that updates after each guess
- Guess history
- Reset button to start over
- Uses champion data from an Excel file

## Project Structure

```text
loldle-solver/
├── app.py
├── Loldle Data.xlsx
├── requirements.txt
├── templates/
│   └── index.html
└── static/
    └── style.css