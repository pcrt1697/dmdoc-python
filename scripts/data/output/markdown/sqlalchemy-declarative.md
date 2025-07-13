
SQLAlchemy Model - Declarative mapping
======================================

Index
=====

* [Entities](#entities)
	* [users](#users)
	* [addresses](#addresses)
	* [credit_cards](#credit_cards)
	* [products](#products)
	* [orders](#orders)
	* [order_items](#order_items)
	* [countries](#countries)
* [Objects](#objects)
* [Enums](#enums)
	* [CountryEnum](#countryenum)
	* [CardVendor](#cardvendor)
	* [OrderStatus](#orderstatus)


**Schema identifier**: *SQLAlchemy Model - Declarative mapping*
# Entities

## users
  
*Aliases:*  
- source.sqlalchemy_model:User


Table that contains all users
### List of fields

|Field name|Data type|Required|Description|
| :---: | :---: | :---: | :---: |
|``id``|string|:heavy_check_mark:|User email that represents the user identifier|
|**name**|string| | |
|**ts_insert**|datetime|:heavy_check_mark:| |
|**ts_update**|datetime|:heavy_check_mark:| |

### Referenced by


- [addresses](#addresses)
    - id: id_user
- [credit_cards](#credit_cards)
    - id: id_user
- [orders](#orders)
    - id: id_user

## addresses
  
*Aliases:*  
- source.sqlalchemy_model:Address

### List of fields

|Field name|Data type|Required|Description|
| :---: | :---: | :---: | :---: |
|``id``|integer|:heavy_check_mark:| |
|**id_user**|string|:heavy_check_mark:| |
|**country**|[CountryEnum](#countryenum)|:heavy_check_mark:|Country identifier|
|**location**|string|:heavy_check_mark:|Address name|
|**city**|string|:heavy_check_mark:|City name|
|**ts_insert**|datetime|:heavy_check_mark:| |
|**ts_update**|datetime|:heavy_check_mark:| |

### External references


- [users](#users)
    - id_user: id

## credit_cards
  
*Aliases:*  
- source.sqlalchemy_model:CreditCard

### List of fields

|Field name|Data type|Required|Description|
| :---: | :---: | :---: | :---: |
|``id``|integer|:heavy_check_mark:| |
|**vendor**|[CardVendor](#cardvendor)|:heavy_check_mark:|Vendor identifier|
|**number**|string|:heavy_check_mark:|Card number|
|**expiration_date**|date|:heavy_check_mark:| |
|**id_user**|string|:heavy_check_mark:| |
|**ts_insert**|datetime|:heavy_check_mark:| |
|**ts_update**|datetime|:heavy_check_mark:| |

### External references


- [users](#users)
    - id_user: id

## products
  
*Aliases:*  
- source.sqlalchemy_model:Product

### List of fields

|Field name|Data type|Required|Description|
| :---: | :---: | :---: | :---: |
|``id``|integer|:heavy_check_mark:| |
|**name**|string|:heavy_check_mark:|Product name|
|**description**|string| |Description of the product|
|**price**|number|:heavy_check_mark:| |
|**height**|number| | |
|**width**|number| | |
|**image**|bytes|:heavy_check_mark:| |
|**ts_insert**|datetime|:heavy_check_mark:| |
|**ts_update**|datetime|:heavy_check_mark:| |

### Referenced by


- [order_items](#order_items)
    - id: id_product

## orders
  
*Aliases:*  
- source.sqlalchemy_model:Order

### List of fields

|Field name|Data type|Required|Description|
| :---: | :---: | :---: | :---: |
|``id``|integer|:heavy_check_mark:| |
|**id_user**|string|:heavy_check_mark:| |
|**status**|[OrderStatus](#orderstatus)|:heavy_check_mark:| |
|**confirmation_date**|datetime| | |
|**shipping_date**|datetime| | |
|**delivery_date**|datetime| | |
|**ts_insert**|datetime|:heavy_check_mark:| |
|**ts_update**|datetime|:heavy_check_mark:| |

### External references


- [users](#users)
    - id_user: id

### Referenced by


- [order_items](#order_items)
    - id: id_order

## order_items
  
*Aliases:*  
- source.sqlalchemy_model:OrderItem

### List of fields

|Field name|Data type|Required|Description|
| :---: | :---: | :---: | :---: |
|``id``|integer|:heavy_check_mark:| |
|**id_order**|integer|:heavy_check_mark:| |
|**id_product**|integer|:heavy_check_mark:| |
|**quantity**|integer|:heavy_check_mark:| |

### External references


- [orders](#orders)
    - id_order: id
- [products](#products)
    - id_product: id

## countries


An example of imperative mapping
### List of fields

|Field name|Data type|Required|Description|
| :---: | :---: | :---: | :---: |
|``id``|integer|:heavy_check_mark:| |
|**name**|[CountryEnum](#countryenum)| | |

# Objects


No object is defined
# Enums

## CountryEnum
  
*Aliases:*  
- source.sqlalchemy_model.CountryEnum

### Values


* **DE**
* **IT**
* **US**
## CardVendor
  
*Aliases:*  
- source.sqlalchemy_model.CardVendor

### Values


* **MASTERCARD**
* **AMERICAN_EXPRESS**
* **VISA**
## OrderStatus
  
*Aliases:*  
- source.sqlalchemy_model.OrderStatus

### Values


* **CREATED [2]**
* **DELIVERED [4]**
* **SHIPPED [3]**
* **DRAFT [1]**