# lb_assignment


Architecture of the code:

Libraries used:

	1. requests - for getting the response from the website.
	2. lxml - For parsing data from html content from the webpage.
	3. pymongo - for creating database and copying data.
	4. urllib retry method - Used to retry when the response is not 200.
	5. JSON - to parse the json data in the webpage.



The code is divided into one class "Crawler" with 4 functions:
	
	1. fetch_company_index 

		- This function crawls for all the company listing pages and saves all the comapny names and company urls to a file.
		- The listing_url format "listing_url = f"https://www.adapt.io/directory/industry/telecommunications/{alphabets_list[i]}-{page_number}".
		- The alphabet and the pagenumber are the inputs for the url.
		- xpath's used to fetch the data:
			company_name = root.xpath('//a[@class="list-link"]/text()')
            		company_url = root.xpath('//a[@class="list-link"]/@href')
        	- This function returns a list "company_profiles_list" and in the end we dump this list to a json file ["comapany_index.json"]`.

    2. fetch_company_details_url_reponse

    	- The input for this fucntion is the file generated above.
    	- this function iterates over each record in the file and get the response and call the extraction function ("fetch_company_details_extraction") to parse the data
    	- The xpath used to fetch the main json data:
    		- company_data = root.xpath("//script[@type='application/json']/text()")[0]

    3. fetch_company_details_extraction

    	- this function is called from function 2 after getting the response.
    	- This function returns a list "company_profiles_list" and in the end we dump this list to a json file ["company_profiles.json"]


    4. write_data_to_db:

    	- Database Used - MongoDB
    	- This function is used to create databases and collections.
    	- We create a database "lb_Assignment" 
    	- Then we create two different coolections called
    		- comapany-index
    		- comapny-profiles
    	- This function also writes data to database.

* * I haven't used any threads because i have no proxies there is high chance of the website blocking me completely

Data Points collected :
	
	1. company name
	2. company location
	3. company website
	4. company webdomain
	5. company industry
	6. company employee_size
	7. company revenue
	8. company description
	9. contact details
		1. contact_name
		2. contact_jobtitle
		3. contact_email_domain
		4. contact_email_domain
	10. similar companies  


Why mongoDB ?:
	
	- High perfomance
	- Highly scalable
	- Very dynamic - No particular schema required
	- Since the data output for the code is json and mongodb uses json in data representation
