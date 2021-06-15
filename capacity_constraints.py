import pandas as pd
import json
from tabulate import tabulate

def load_offers(project_id="all"):
    #Read offers from file for testing
    offers = pd.read_csv("./offers.csv")
    offers = offers[offers["Item"].isna()==False]
    offers = offers[offers["Project"].isna()==False]
    offers["Capacity"] = offers["Capacity"].fillna(0).astype(int)
    
    if project_id == "all":
        return offers
    else:
        return offers[offers["Project"]==project_id]
    
    
def load_bundle_capacities(project_id="all"):
    bundle_constraints = pd.read_csv("./bundle_capacities.csv", sep=";")

    if project_id == "all":
        return bundle_constraints
    else:
        return bundle_constraints[bundle_constraints["Project"]==project_id]

def get_single_item_capacity_constraints(offers):
    result_df = offers[["Supplier", "Item", "Capacity", "Project"]].copy()
    result_df["ConstraintType"] = "SingleItem"
    result_df["Item"] = result_df["Item"].apply(lambda x: x.split())
    result_df["BundleConstraintOriginal"] = None
    return result_df

def get_bundle_item_capacity_constraints(offers, bundle_capacities):
    result_df = pd.DataFrame()
    for index, row in bundle_capacities.iterrows():
        offer_filter = json.loads(row["Condition"])
        relevant_offers = pd.DataFrame() #initialize empty
        try:
            relevant_offers = offers[offers["Supplier"]==row["Supplier"]].loc[(offers[list(offer_filter)] == pd.Series(offer_filter, dtype=str)).all(axis=1)]
            temp = relevant_offers.groupby(["Project", "Supplier"])["Item"].unique().reset_index()
            temp["Capacity"] = row["Capacity"]
            temp["Project"] = row["Project"]
            temp["ConstraintType"] = "Bundle" if len(offer_filter) > 0 else "Global"
            temp["BundleConstraintOriginal"] = str(offer_filter)
            result_df = result_df.append(temp)
        
        except KeyError as e:
            print(f'Bad constraint" {offer_filter} will be ignored. Key(s) not in offers')
            
    return result_df


def get_all_capacity_constraints(offers, bundle_capacities=None):
    single = get_single_item_capacity_constraints(offers)
    
    if bundle_capacities is None:
        return single
    else:
        bundle = get_bundle_item_capacity_constraints(offers, bundle_capacities)
        return single.append(bundle).reset_index(drop=True)
    
if __name__ == "__main__":
    offers_table = load_offers("33aad28d")
    bundle_capacities_table = load_bundle_capacities("33aad28d")
    final_capacities_table = get_all_capacity_constraints(offers_table, bundle_capacities_table)
    print(tabulate(final_capacities_table, headers='keys', tablefmt='github'))