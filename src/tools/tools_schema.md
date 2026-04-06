# Tool Schema for React Agent

This document describes the available mock drug database and helper functions implemented in `tools.py`. It is intended to help integrate the Python backend with a React agent by clarifying inputs, outputs, and behavior.

## Mock Database: `medicines`

A dictionary where each key is a medicine name and each value is a dictionary with the following fields:

- `name`: string
- `dose_adults`: string
- `dose_children`: string
- `category`: string
- `contraindications`: string
- `main_active_ingredient`: string

### Example entry

```python
"Aspirin": {
    "name": "Aspirin",
    "dose_adults": "325-650mg every 4-6 hours",
    "dose_children": "Not recommended for children under 16",
    "category": "Analgesic",
    "contraindications": "Allergy to aspirin, bleeding disorders, ulcers",
    "main_active_ingredient": "Acetylsalicylic acid"
}
```

## Helper Functions

### `search_drug(drug_name)`

Lookup a medicine by name.

#### Input

- `drug_name`: string

#### Output

- returns a medicine dictionary if found
- returns `None` if no matching drug is found or if `drug_name` is not a string

#### Notes

- Matching is case-insensitive and trims whitespace.

### `check_interaction(drug1, drug2)`

Check whether two medicines may interact based on category rules.

#### Input

- `drug1`: string
- `drug2`: string

#### Output

A dictionary with these fields:

- `drug1`: string
- `drug2`: string
- `interaction`: string
- `message`: string
- `category1`: string (when available)
- `category2`: string (when available)

#### Possible interaction values

- `dangerous`
- `moderate`
- `caution`
- `low`
- `same drug`
- `unknown`

#### Example result

```python
{
    "drug1": "Warfarin",
    "drug2": "Ibuprofen",
    "interaction": "dangerous",
    "message": "NSAIDs can increase the risk of bleeding when taken with anticoagulants.",
    "category1": "Anticoagulant",
    "category2": "Non-steroidal anti-inflammatory drug (NSAID)"
}
```

### `calculate_dose(drug_name, weight_kg, age_years)`

Calculate a dose recommendation based on the user's weight and age.

#### Input

- `drug_name`: string
- `weight_kg`: positive number
- `age_years`: non-negative number

#### Output

If the drug is found and inputs are valid, returns a dictionary with:

- `drug`: string
- `age_group`: string (`adult` or `child`)
- `weight_kg`: number
- `recommended_dose`: string
- `calculated_dose`: string
- `note`: string (only for non-weight-based doses)

If inputs are invalid, returns a dictionary with:

- `drug`: string
- `error`: string

If the drug is not found, returns `None`.

#### Behavior

- If `age_years < 16`, the child dose is used.
- Otherwise, the adult dose is used.
- If the selected dose text contains `mg/kg`, the function computes a weight-based range.
- For standard adult doses without `mg/kg`, the function returns the dose string unchanged.

#### Example result

```python
{
    "drug": "Ibuprofen",
    "age_group": "child",
    "weight_kg": 20,
    "recommended_dose": "5-10mg/kg every 6-8 hours",
    "calculated_dose": "100-200mg every 6-8 hours"
}
```

## Integration Notes for React Agent

- React cannot call this Python module directly in the browser.
- Use a backend API layer (e.g. Flask, FastAPI, Django, or another Python web service) to expose these helper functions.
- Return JSON responses from the backend so the React agent can consume them easily.
- Keep the database and logic in the Python backend, and use the React app only for client-side interaction.

## Recommended API endpoints

- `GET /api/search?drug=<name>`
- `GET /api/interaction?drug1=<name>&drug2=<name>`
- `POST /api/dose` with JSON body `{"drug": "Ibuprofen", "weight_kg": 20, "age_years": 10}`

## Disclaimer

The database and interaction logic are mock/sample implementations. They are not a substitute for medical advice.
