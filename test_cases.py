import json


## Test case 1 - validates if we have same count of data in listing and product crawl.


def validating_counts():
    with open("company_index.json") as f:
        for each in f:
            data = json.loads(each)
            company_index_count = len(data)

    with open("company_profiles.json") as f:
        for each in f:
            data = json.loads(each)
            company_profiles_count = len(data)

    assert company_index_count == company_profiles_count, "counts should be equal"
    

## Test case 2 - validates the count of companies in both files
def checking_companies():
    company_index_list = []
    with open("company_index.json") as f:
        for each in f:
            data = json.loads(each)
            for i in data:
                company_index_list.append((i.get("company_name")))

    company_profiles_list = []
    with open("company_profiles.json") as f:
        for each in f:
            data = json.loads(each)
            for i in data:
                company_profiles_list.append((i.get("company_name")))

    assert len(company_index_list) == len(company_profiles_list), "companies missing"

if __name__ == "__main__":
    validating_counts()
    checking_companies()
    print("Everything passed")