# LoLdle Solver

A simple Flask web app that helps solve LoLdle champion guesses. Enter a champion guess and select the feedback colors for each category. The app filters the possible champions and keeps a guess history until you reset.

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