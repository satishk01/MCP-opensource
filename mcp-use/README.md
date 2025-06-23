"# MCP-opensource" 

## instal uv
curl -LsSf https://astral.sh/uv/install.sh | sh

#install git nodejs and npm
sudo yum update
sudo yum install git nodejs npm  -y

### create a direcvtory and activate python 3.12
mkdire demo
cd demo
uv venv --python 3.12
source .venv/bin/activate


### install required dependencies
uv pip install -r requirements.txt


### basic App
python app.py

## streamlit app
streamlit run streamlit-app.py
