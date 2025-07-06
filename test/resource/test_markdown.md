
sample_schema
=============

Index
=====

* [Entities](#entities)
	* [samples](#samples)
	* [ReferencedDocument](#referenceddocument)
* [Objects](#objects)
	* [NestedObject](#nestedobject)
* [Enums](#enums)
	* [SampleEnum](#sampleenum)

# Entities

## samples
  
*Aliases:*  
- source.beanie_model.SampleDocument


Sample docstring
### List of fields

|Field name|Data type|Required|Description|
| :---: | :---: | :---: | :---: |
|**id**|objectId| |MongoDB document ObjectID|
|**string_field**|string|:heavy_check_mark:|Sample description|
|**bool_field**|boolean|:heavy_check_mark:| |
|**bytes_field**|bytes|:heavy_check_mark:| |
|**float_field**|number|:heavy_check_mark:| |
|**decimal_field**|number|:heavy_check_mark:| |
|**integer_field**|integer|:heavy_check_mark:| |
|**datetime_field**|datetime|:heavy_check_mark:| |
|**date_field**|date|:heavy_check_mark:| |
|**time_field**|time|:heavy_check_mark:| |
|**enum_field**|SampleEnum|:heavy_check_mark:| |
|**union_field**|union[integer, string]|:heavy_check_mark:| |
|**optional_field**|string|:heavy_check_mark:| |
|**map_field**|array[string]|:heavy_check_mark:| |
|**list_array_field**|array[string]|:heavy_check_mark:| |
|**set_array_field**|array[string]|:heavy_check_mark:| |
|**tuple_array_field**|array[string]|:heavy_check_mark:| |
|**object_field**|NestedObject|:heavy_check_mark:| |
|**mixed_array_field**|array[union[integer, string]]|:heavy_check_mark:| |

### External references


- [ReferencedDocument](#referenceddocument)
    - string_field: _id

## ReferencedDocument
  
*Aliases:*  
- source.beanie_model.ReferencedDocument

### List of fields

|Field name|Data type|Required|Description|
| :---: | :---: | :---: | :---: |
|**id**|objectId| |MongoDB document ObjectID|

### External references



# Objects

## NestedObject
  
*Aliases:*  
- source.beanie_model.NestedObject

### List of fields

|Field name|Data type|Required|Description|
| :---: | :---: | :---: | :---: |
|**string_field**|string|:heavy_check_mark:| |

### External references



# Enums

## SampleEnum
  
*Aliases:*  
- source.beanie_model.SampleEnum

### Values


* **first**
* **second**
* **third**