"# MCP-opensource" 

## instal uv
curl -LsSf https://astral.sh/uv/install.sh | sh

#install git nodejs and npm
sudo yum update
sudo yum install git nodejs npm  -y

sudo npm install -g @executeautomation/playwright-mcp-server

### create a direcvtory and activate python 3.12
mkdire demo
cd demo
uv venv --python 3.12
source .venv/bin/activate


### install required dependencies
uv pip install -r requirements.txt

# create file browser_mcp.json

## streamlit app
streamlit run app.py



Sample commans to test


####Get Command Prompt
Send GET request with end pointhttps://api.restful-api.dev/objects to fetch all objects and Validate response
Check if status is 200
Ensure response body is an array
Shwo teh response details



####Post Command Prompt
Perform POST operation for the url https://api.restful-api.dev/objects

Pass below data into body 

{
   "name": "Apple MacBook M4 Pro 16",
   "data": {
      "year": 2025,
      "price": 6849.99,
      "CPU model": "Intel Core i12",
      "Hard disk size": "1 TB"
   }
}

Verify the response body contain id and createdAt 
and Saved the generated id in variable id

####PUT Command Prompt

Perform PUT operation with using save id  @https://api.restful-api.dev/objects/id

Pass below data into body 

{
   "name": "Apple MacBook Pro 89",
   "data": {
      "year": 2025,
      "price": 123.99,
      "CPU model": "Intel Core i11",
      "Hard disk size": "10TB"
   }
}

Show the data changes before and after updates

####GET Command Prompt

Perform GET operation with using save id  @https://api.restful-api.dev/objects/id

####Delete Command Prompt

Perform DELETE operation with using save id  @https://api.restful-api.dev/objects/id
