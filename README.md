# Input format

## Table "offers" (including item level capacities)

|    | Item      | Supplier   |   Unit Price | Project   | Type     | CountrySupplier   | Region       | CountryDestination   |   Capacity | PackagingType   |
|----|-----------|------------|--------------|-----------|----------|-------------------|--------------|----------------------|------------|-----------------|
|  0 | Item_0001 | Clariant   |       187.27 | 33aad28d  | Standard | USA               | Asia         | India                |      26089 | TypeZero        |
|  1 | Item_0001 | DuPont     |       199.09 | 33aad28d  | Standard | USA               | Asia         | India                |       5391 | BetaPackaging   |
|  2 | Item_0002 | BASF       |       225.68 | 33aad28d  | Standard | USA               | SouthAmerica | Mexico               |      49576 | Pack1           |
|  3 | Item_0002 | DuPont     |       235.57 | 33aad28d  | Standard | USA               | SouthAmerica | Mexico               |      48661 | BetaPackaging   |
|  4 | Item_0002 | SABIC      |       200.27 | 33aad28d  | Standard | Chile             | Europe       | Germany              |      49761 | AlphaPackaging  |
|  5 | Item_0003 | BASF       |       213.14 | 33aad28d  | Critical | Chile             | Europe       | Germany              |      35099 | Pack1           |
|  6 | Item_0003 | DuPont     |       165.85 | 33aad28d  | Critical | India             | SouthAmerica | Mexico               |      12661 | AlphaPackaging  |
|  7 | Item_0003 | INEOS      |       219.17 | 33aad28d  | Critical | India             | SouthAmerica | Mexico               |      23567 | TypeOne         |
|  8 | Item_0003 | SABIC      |       211.18 | 33aad28d  | Critical | India             | SouthAmerica | Mexico               |       4434 | TypeTwo         |


## Table "bundle_capacities" (includes both global and bundle capacities)
**Idea:** 
- having both global and bundle capacities in 1 table, because global capacities can be regarded as a special type of bundle capacities
- Using JSON to specify conditions, which integrates well to JS web applications and Python dictionaries, which have O(1) time complexity for search, insertion and deletion

|    | Project   | Supplier   |   Capacity | Condition                                                             |
|----|-----------|------------|------------|-----------------------------------------------------------------------|
|  0 | 33aad28d  | Clariant   |       2000 | {"CountrySupplier":"USA"}                                             |
|  1 | 33aad28d  | DuPont     |       3000 | {"PackagingType":"BetaPackaging","Type":"Standard"}                   |
|  2 | 33aad28d  | INEOS      |       3000 | {"Type":"Critical","Region":"SouthAmerica","PackagingType":"TypeOne"} |
|  3 | 33aad28d  | DuPont     |       3000 | {}                                                                    |
|  4 | 33aad28d  | SABIC      |       3000 | {}                                                                    |

**In this example:**
- Line 0 is a conditional capacity constraint with 1 constraint for CountrySupplier = "USA"
- Line 1 is a conditional capacity constraint with 2 "AND" constraints PackagingType = "BetaPackaging" AND Type = "Standard"
- Line 2 is a conditional capacity constraint with 3 "AND" constraints ...
- Line 3 and 4 are global constraints (no condition --> applies to all items)


# Data flow

- Buyer submits list of offers (including item level capacities) --> stored in the database as table "offers" see schema above
- Buyer submits additional global and bundle capacities (optional) --> stored in the database as table "bundle_capacities" see schema above
- Python module loads table "offers" WHERE Project = "abc"
- Python module loads table "bundle_capacities" WHERE Project = "abc"
- Python module implements function get_single_item_capacity_constraints(), which selects the item level capacities from the offers table
- Python module implements function get_bundle_item_capacity_constraints(), which translates bundle capacities of filter columns into item level capacities (array of items)
- Python modules writes table "final_capacities" to database see schema below
- Linear program loads "final_capacities" from database and uses them as constraints

# Output table "final_capacities"
**Idea:**
- all capacties (item level, global, bundle) in 1 table 
- items are represented as an array, multiple elements within the array represent global or bundle constraints, while single item array are simple item level constraints 

|    | Supplier   | Item                                  |   Capacity | Project   | ConstraintType   | BundleConstraintOriginal                                                   |
|----|------------|---------------------------------------|------------|-----------|------------------|----------------------------------------------------------------------------|
|  0 | Clariant   | ['Item_0001']                         |      26089 | 33aad28d  | SingleItem       |                                                                            |
|  1 | DuPont     | ['Item_0001']                         |       5391 | 33aad28d  | SingleItem       |                                                                            |
|  2 | BASF       | ['Item_0002']                         |      49576 | 33aad28d  | SingleItem       |                                                                            |
|  3 | DuPont     | ['Item_0002']                         |      48661 | 33aad28d  | SingleItem       |                                                                            |
|  4 | SABIC      | ['Item_0002']                         |      49761 | 33aad28d  | SingleItem       |                                                                            |
|  5 | BASF       | ['Item_0003']                         |      35099 | 33aad28d  | SingleItem       |                                                                            |
|  6 | DuPont     | ['Item_0003']                         |      12661 | 33aad28d  | SingleItem       |                                                                            |
|  7 | INEOS      | ['Item_0003']                         |      23567 | 33aad28d  | SingleItem       |                                                                            |
|  8 | SABIC      | ['Item_0003']                         |       4434 | 33aad28d  | SingleItem       |                                                                            |
|  9 | Clariant   | ['Item_0001']                         |       2000 | 33aad28d  | Bundle           | {'CountrySupplier': 'USA'}                                                 |
| 10 | DuPont     | ['Item_0001' 'Item_0002']             |       3000 | 33aad28d  | Bundle           | {'PackagingType': 'BetaPackaging', 'Type': 'Standard'}                     |
| 11 | INEOS      | ['Item_0003']                         |       3000 | 33aad28d  | Bundle           | {'Type': 'Critical', 'Region': 'SouthAmerica', 'PackagingType': 'TypeOne'} |
| 12 | DuPont     | ['Item_0001' 'Item_0002' 'Item_0003'] |       3000 | 33aad28d  | Global           | {}                                                                         |
| 13 | SABIC      | ['Item_0002' 'Item_0003']             |       3000 | 33aad28d  | Global           | {}                                                                         |