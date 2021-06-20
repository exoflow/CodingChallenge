import pandas as pd
import json
from tabulate import tabulate
from sqlalchemy import create_engine

### Database functions ###

def db_load_bundle_capacities(project_id: str) -> dict:
    try:
        #Todo: finish function
        pass
        #engine = create_engine('postgresql://...')
        #query=f'SELECT * FROM bundle_capacities WHERE project_id = '{project_id}'"
        #bundle_capacities = pd.to_dict(pd.read_sql_query(query, engine))
    except Exception as e:
        bundle_capacities = dict()
        print(e)

    return bundle_capacities

def db_update_bundle_capacities(bundle_capacities: dict) -> bool:
    project_id = bundle_capacities["project_id"]
    try:
        #Todo: finish function
        #engine = create_engine('postgresql://...')
        #query=f'DELETE FROM bundle_capacities WHERE project_id = '{project_id}';"
        #engine.execute(query)
        #pd.DataFrame.from_dict(bundle_capacities).to_sql(if_exists="append")
        success = True
    except Exception as e:
        success = False
        print(e)

    return success

### Capacity functions ###

def get_single_item_capacities(offers: dict) -> dict:
    single_item_capacities = {}
    single_item_capacities["data"] = [{"Supplier":offer["Supplier"], "Project":offer["Project"], "Item":offer["Item"], "Capacity":offer["Capacity"]} for offer in input_offers["data"]]
    return single_item_capacities


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
        
    
if __name__ == "__main__":
    #Using JSON file for testing
    with open('./input_offers.json') as input_offers_file:
        input_offers = json.load(input_offers_file)

    with open('./input_bundle_capacities.json') as input_bundle_capacities_file:
        input_bundle_capacities = json.load(input_bundle_capacities_file)

    #Pretty printing the dictionary as tabular data
    bundle_item_capacities = pd.DataFrame(get_bundle_item_capacities(input_bundle_capacities, input_offers)["data"])
    print(tabulate(bundle_item_capacities, bundle_item_capacities.columns, tablefmt="github")) 
