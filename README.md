# 1 Coding challenge ideas and implementation

## 1 User Input

Assumption: Users (buyers, suppliers) upload data via file or enter it manually via web app. The data volume is "small" (few thousand rows), so the input can be parsed to JSON within a few seconds. The JSON format is required to communicate with the Python module. However, the "user friendly" input can be different from the required JSON format. I think this decision is subject to usability testing / user feedback therefore I did not focus on it.

## 2 Input format for Python module

### 2.1 `bundle_capacities`: Global and bundle capacity constraints

```javascript
{
    "project_id": "33aad28d",
    "data": [
        {
            "Supplier": "Clariant",
            "Capacity": 2000,
            "Condition": {
                "CountrySupplier": "USA"
            }
        },
        {
            "Supplier": "DuPont",
            "Capacity": 3000,
            "Condition": {
                "PackagingType": "BetaPackaging",
                "Type": "Standard"
            }
        },
        {
            "Supplier": "INEOS",
            "Capacity": 3000,
            "Condition": {
                "Type": "Critical",
                "Region": "SouthAmerica",
                "PackagingType": "TypeOne"
            }
        },
        {
            "Supplier": "DuPont",
            "Capacity": 3000,
            "Condition": {}
        },
        {
            "Supplier": "SABIC",
            "Capacity": 3000,
            "Condition": {}
        }
    ]
}
```

**Idea:**

- global and bundle capacities have the same input format, because global capacities can be regarded as a special type of bundle capacities. The only difference is the `Condition` key, which is empty for global capacity constraints
- Using JSON integrates well with the web app (parsing files) and Python dictionaries, which have O(1) time complexity for search, insertion and deletion. The child keys within the `Condition` key are very flexible. 

### 2.2 Offers

```javascript
{
  "project_id": "33aad28d",
  "data": [
    {
      "OfferId": 1,
      "Item": "Item_0001",
      "Supplier": "Clariant",
      "Unit Price": 187.27,
      "Type": "Standard",
      "CountrySupplier": "USA",
      "Region": "Asia",
      "CountryDestination": "India",
      "Capacity": 26089,
      "PackagingType": "TypeZero"
    },
    {
      "OfferId": 2,
      "Item": "Item_0001",
      "Supplier": "DuPont",
      "Unit Price": 199.09,
      "Type": "Standard",
      "CountrySupplier": "USA",
      "Region": "Asia",
      "CountryDestination": "India",
      "Capacity": 5391,
      "PackagingType": "BetaPackaging"
    },
    {
      "OfferId": 3,
      "Item": "Item_0002",
      "Supplier": "BASF",
      "Unit Price": 225.68,
      "Type": "Standard",
      "CountrySupplier": "USA",
      "Region": "SouthAmerica",
      "CountryDestination": "Mexico",
      "Capacity": 49576,
      "PackagingType": "Pack1"
    },
    {
      "OfferId": 4,
      "Item": "Item_0002",
      "Supplier": "DuPont",
      "Unit Price": 235.57,
      "Type": "Standard",
      "CountrySupplier": "USA",
      "Region": "SouthAmerica",
      "CountryDestination": "Mexico",
      "Capacity": 48661,
      "PackagingType": "BetaPackaging"
    },
    {
      "OfferId": 5,
      "Item": "Item_0002",
      "Supplier": "SABIC",
      "Unit Price": 200.27,
      "Type": "Standard",
      "CountrySupplier": "Chile",
      "Region": "Europe",
      "CountryDestination": "Germany",
      "Capacity": 49761,
      "PackagingType": "AlphaPackaging"
    },
    {
      "OfferId": 6,
      "Item": "Item_0003",
      "Supplier": "BASF",
      "Unit Price": 213.14,
      "Type": "Critical",
      "CountrySupplier": "Chile",
      "Region": "Europe",
      "CountryDestination": "Germany",
      "Capacity": 35099,
      "PackagingType": "Pack1"
    },
    {
      "OfferId": 7,
      "Item": "Item_0003",
      "Supplier": "DuPont",
      "Unit Price": 165.85,
      "Type": "Critical",
      "CountrySupplier": "India",
      "Region": "SouthAmerica",
      "CountryDestination": "Mexico",
      "Capacity": 12661,
      "PackagingType": "AlphaPackaging"
    },
    {
      "OfferId": 8,
      "Item": "Item_0003",
      "Supplier": "INEOS",
      "Unit Price": 219.17,
      "Type": "Critical",
      "CountrySupplier": "India",
      "Region": "SouthAmerica",
      "CountryDestination": "Mexico",
      "Capacity": 23567,
      "PackagingType": "TypeOne"
    },
    {
      "OfferId": 9,
      "Item": "Item_0003",
      "Supplier": "SABIC",
      "Unit Price": 211.18,
      "Type": "Critical",
      "CountrySupplier": "India",
      "Region": "SouthAmerica",
      "CountryDestination": "Mexico",
      "Capacity": 4434,
      "PackagingType": "TypeTwo"
    }
  ]
}
```

## 3 Python functions

### 3.1 Adding `Item` and `OfferId` to bundle_capacities input

```python
### Runtime is around 500 ms for an input of 1000 bundle capacties and 1000 offers
def get_bundle_item_capacities(bundle_capacities: dict, offers:dict) -> dict:
    bundle_item_capacities = bundle_capacities.copy()
    
    for bundle_capacity in bundle_item_capacities["data"]:
        condition = bundle_capacity["Condition"]
        
        #Global
        if condition == {}:
            relevant_items = set(offer["Item"] for offer in offers["data"] if offer["Supplier"] == bundle_capacity["Supplier"])
            relevant_offer_ids = set(offer["OfferId"] for offer in offers["data"] if offer["Supplier"] == bundle_capacity["Supplier"])
        
        #Bundle
        else:
            for attribute, value in condition.items():    
                relevant_items = set(offer["Item"] for offer in offers["data"] if (offer["Supplier"] == bundle_capacity["Supplier"] and offer[attribute] == value))
                relevant_offer_ids = set(offer["OfferId"] for offer in offers["data"] if (offer["Supplier"] == bundle_capacity["Supplier"] and offer[attribute] == value))

        bundle_capacity["Item"] = relevant_items
        bundle_capacity["OfferId"] = relevant_offer_ids
    
    return bundle_item_capacities
        
```

**Performance comparison:** The dataframe based function below is shorter and seems to have fewer for loops, however it takes 6x longer than the dictionary based function above.

```python
### Runtime is around 3 seconds for an input of 1000 bundle capacties and 1000 offers
def get_bundle_item_capacities(bundle_capacities: dict, offers:dict) -> dict:
    bundle_item_capacities = bundle_capacities.copy()
    df_bundle_capacities= pd.DataFrame(bundle_capacities["data"])
    df_offers = pd.DataFrame(offers["data"])

    for index, row in pd.DataFrame(df_bundle_capacities).iterrows():
        #Filter for supplier and condition
        relevant_items = df_offers[df_offers["Supplier"]==row["Supplier"]][["Item", "OfferId"]] 
        relevant_items = relevant_items.loc[(df_offers[list(row["Condition"])] == pd.Series(row["Condition"], dtype=str)).all(axis=1)]
        #Add columns to dict
        bundle_item_capacities["data"][index]["Items"] = set(sorted(relevant_items["Item"]))
        bundle_item_capacities["data"][index]["OfferIds"] = set(sorted(relevant_items["OfferId"]))
    
    return bundle_item_capacities
```

### 3.2 Getting single item capacities from offers

```python
def get_single_item_capacities(offers: dict) -> dict:
    single_item_capacities = {}
    single_item_capacities["project_id"] = offers["project_id"]
    single_item_capacities["data"] = [{"Supplier":offer["Supplier"], "Capacity":offer["Capacity"], "Item":offer["Item"], "OfferId":offer["OfferId"], } for offer in input_offers["data"]]
    return single_item_capacities
```

## 4. Using single_item_capacities and bundle_item_capacities for efficient lookups

- fetching all regional and global capacities with the offers they are connected to:

```python
get_bundle_item_capacities(input_bundle_capacities, input_offers)["data"]
```

- fetching all capacities a certain offer is subject to:

```python
offer_id = 4 #also works with an item name: item = "Item_0001"
bundle_item_capacities = get_bundle_item_capacities(input_bundle_capacities, input_offers)["data"]
[constraint for constraint in bundle_item_capacities if offer_id in constraint["OfferId"]]
```

**Further improvements:**
The offer_ids for a bundle capacity constraint are collected in a set() as data structure which has lookups (as well as insert and delete) in O(1). However, the capacity objects are collected in a list which is looped through in O(n) time. For further performance improvements the `bundle_item_capacities` dictionary can be rearragned to use `OfferIds` or `Item` as a key which will speed up lookups for a specific offer (but won't increase performance when all regional and global capacities are fetched).

## 5. Persisting capacities in a relational database

- dictionaries can be easily converted to tabular data and stored in a relational database. For example:

```python
pd.DataFrame(bundle_item_capacities)
```

|    | Supplier   |   Capacity | Condition                                                                  | Item                                    | OfferId   |
|----|------------|------------|----------------------------------------------------------------------------|-----------------------------------------|-----------|
|  0 | Clariant   |       2000 | {'CountrySupplier': 'USA'}                                                 | {'Item_0001'}                           | {1}       |
|  1 | DuPont     |       3000 | {'PackagingType': 'BetaPackaging', 'Type': 'Standard'}                     | {'Item_0001', 'Item_0002'}              | {2, 4}    |
|  2 | INEOS      |       3000 | {'Type': 'Critical', 'Region': 'SouthAmerica', 'PackagingType': 'TypeOne'} | {'Item_0003'}                           | {8}       |
|  3 | DuPont     |       3000 | {}                                                                         | {'Item_0001', 'Item_0002', 'Item_0003'} | {2, 4, 7} |
|  4 | SABIC      |       3000 | {}                                                                         | {'Item_0002', 'Item_0003'}              | {9, 5}    |

- It's also possible to explode the Condition column to store atomic values but this can cause many null values and therefore inefficient storage

```python
pd.json_normalize(bundle_item_capacities).fillna("")
```

|    | Supplier   |   Capacity | Item                                    | OfferId   | Condition.CountrySupplier   | Condition.PackagingType   | Condition.Type   | Condition.Region   |
|----|------------|------------|-----------------------------------------|-----------|-----------------------------|---------------------------|------------------|--------------------|
|  0 | Clariant   |       2000 | {'Item_0001'}                           | {1}       | USA                         |                           |                  |                    |
|  1 | DuPont     |       3000 | {'Item_0001', 'Item_0002'}              | {2, 4}    |                             | BetaPackaging             | Standard         |                    |
|  2 | INEOS      |       3000 | {'Item_0003'}                           | {8}       |                             | TypeOne                   | Critical         | SouthAmerica       |
|  3 | DuPont     |       3000 | {'Item_0001', 'Item_0002', 'Item_0003'} | {2, 4, 7} |                             |                           |                  |                    |
|  4 | SABIC      |       3000 | {'Item_0002', 'Item_0003'}              | {9, 5}    |                             |                           |                  |                    |

## 6. Further ideas and discussion topics

- Single item capacities and bundle item capacities can be unioned into 1 dataset if they are most often needed together
- Storage and compute seperation: When to persist returned data structures in a relational database? Possible consistency issues: what if a database insert fails but the datastructure was returned correctly and is used by the optimization module.
- Input format for the app users: as mentioned in 1. the input format from the users can be different from the parsed JSON. Goal is to make it as simple as possible for the users while requiring a minimum sturcture to parse the input correctly. For example instead of using JSON for the bundle capacities users could use a more SQL like syntax which is then parsed to JSON. How to determine the best input format? Usability tests, user feedback?

```javascript
"Condition": {
  "Type": "Critical",
  "Region": "SouthAmerica",
  "PackagingType": "TypeOne"
}
```

```sql
Type='Critical' AND Region='SouthAmerica' AND PackagingType='TypeOne'
}
```

- Time complexity: What is the usual input size for offers, bundle_capacities and the number of conditions per bundle capacity? There is likely room for improvement of the current implementation of `get_bundle_item_capacities` because it uses 2 for loops and a list comprehension. Is this a bottleneck? What's the runtime of the linear program? 