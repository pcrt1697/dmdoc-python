
Beanie data model
=================

Index
=====

* [Entities](#entities)
	* [users](#users)
	* [products](#products)
	* [orders](#orders)
* [Objects](#objects)
	* [Address](#address)
	* [CreditCard](#creditcard)
	* [AuditMeta](#auditmeta)
	* [OrderItem](#orderitem)
	* [OrderTransaction](#ordertransaction)
* [Enums](#enums)
	* [Country](#country)
	* [CardVendor](#cardvendor)
	* [OrderStatus](#orderstatus)


**Schema identifier**: *Beanie data model*
# Entities

## users
  
*Aliases:*  
- source.beanie_model.User

### List of fields

|Field name|Data type|Required|Description|
| :---: | :---: | :---: | :---: |
|**id**|string|:heavy_check_mark:|User email that represents the user identifier|
|**name**|string|:heavy_check_mark:|Name of the user|
|**address**|[Address](#address)| |First name of the user|
|**credit_cards**|array<[CreditCard](#creditcard)>| |Payment methods saved by user|
|**audit**|[AuditMeta](#auditmeta)|:heavy_check_mark:|Update/insert document metadata|

### Referenced by


- [orders](#orders)
    - credit_cards.number: transaction.credit_card
- [orders](#orders)
    - id: id_user

## products
  
*Aliases:*  
- source.beanie_model.Product

### List of fields

|Field name|Data type|Required|Description|
| :---: | :---: | :---: | :---: |
|**id**|objectId| |MongoDB document ObjectID|
|**name**|string|:heavy_check_mark:|Product name|
|**description**|string| | |
|**price**|number|:heavy_check_mark:| |
|**height**|number|:heavy_check_mark:| |
|**width**|number|:heavy_check_mark:| |
|**additional_names**|array<string>|:heavy_check_mark:| |
|**image**|bytes|:heavy_check_mark:| |
|**properties**|map<string>| |Additional properties of the product|
|**audit**|[AuditMeta](#auditmeta)|:heavy_check_mark:|Update/insert document metadata|

### Referenced by


- [orders](#orders)
    - id: items.id_product

## orders
  
*Aliases:*  
- source.beanie_model.Order

### List of fields

|Field name|Data type|Required|Description|
| :---: | :---: | :---: | :---: |
|**id**|objectId| |MongoDB document ObjectID|
|**id_user**|string|:heavy_check_mark:| |
|**status**|[OrderStatus](#orderstatus)|:heavy_check_mark:| |
|**confirmation_date**|datetime|:heavy_check_mark:| |
|**shipping_date**|datetime|:heavy_check_mark:| |
|**delivery_date**|datetime|:heavy_check_mark:| |
|**items**|array<[OrderItem](#orderitem)>|:heavy_check_mark:|List of products|
|**transaction**|[OrderTransaction](#ordertransaction)|:heavy_check_mark:| |
|**audit**|[AuditMeta](#auditmeta)|:heavy_check_mark:|Update/insert document metadata|

### External references


- [users](#users)
    - transaction.credit_card: credit_cards.number
- [users](#users)
    - id_user: id
- [products](#products)
    - items.id_product: id

# Objects

## Address
  
*Aliases:*  
- source.beanie_model.Address

### List of fields

|Field name|Data type|Required|Description|
| :---: | :---: | :---: | :---: |
|**country**|[Country](#country)|:heavy_check_mark:|Country identifier|
|**location**|string|:heavy_check_mark:|Address name|
|**city**|string|:heavy_check_mark:|City name|

## CreditCard
  
*Aliases:*  
- source.beanie_model.CreditCard

### List of fields

|Field name|Data type|Required|Description|
| :---: | :---: | :---: | :---: |
|**vendor**|[CardVendor](#cardvendor)|:heavy_check_mark:|Vendor identifier|
|**number**|string|:heavy_check_mark:|Card number|
|**expiration_date**|date|:heavy_check_mark:| |

## AuditMeta
  
*Aliases:*  
- source.beanie_model.AuditMeta

### List of fields

|Field name|Data type|Required|Description|
| :---: | :---: | :---: | :---: |
|**ts_insert**|datetime|:heavy_check_mark:|Document creation date|
|**ts_update**|datetime|:heavy_check_mark:|Last update date|

## OrderItem
  
*Aliases:*  
- source.beanie_model.OrderItem

### List of fields

|Field name|Data type|Required|Description|
| :---: | :---: | :---: | :---: |
|**id_product**|objectId|:heavy_check_mark:| |
|**quantity**|integer|:heavy_check_mark:| |

## OrderTransaction
  
*Aliases:*  
- source.beanie_model.OrderTransaction

### List of fields

|Field name|Data type|Required|Description|
| :---: | :---: | :---: | :---: |
|**credit_card**|string|:heavy_check_mark:| |
|**amount**|number|:heavy_check_mark:| |

# Enums

## Country
  
*Aliases:*  
- source.beanie_model.Country

### Values


* **IT**
* **US**
* **DE**
## CardVendor
  
*Aliases:*  
- source.beanie_model.CardVendor

### Values


* **MASTERCARD**
* **AMERICAN_EXPRESS**
* **VISA**
## OrderStatus
  
*Aliases:*  
- source.beanie_model.OrderStatus

### Values


* **DELIVERED [4]**
* **CREATED [2]**
* **DRAFT [1]**
* **SHIPPED [3]**