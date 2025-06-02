
sample_schema
=============

Index
=====

* [user_account](#user_account)
* [address](#address)

# user_account
  
*Aliases:*  
- sqlalchemy_sample.model:User


user_account
## List of fields

|Field name|Data type|Required|Description|
| :---: | :---: | :---: | :---: |
|``id``|string| |id|
|**name**|string| |name|
|**fullname**|string|:heavy_check_mark:|fullname|

## External references



# address
  
*Aliases:*  
- sqlalchemy_sample.model:Address


address
## List of fields

|Field name|Data type|Required|Description|
| :---: | :---: | :---: | :---: |
|``id``|string| |id|
|**email_address**|string| |email_address|
|**user_id**|string| |user_id|

## External references


- [user_account](#user_account)
    - user_id: id
