import frappe
from erpnext.setup.doctype.vehicle.vehicle import Vehicle as BaseVehicle
from frappe import _


class Vehicle(BaseVehicle):
	@staticmethod
	def default_list_data():
		columns = [
			{
				"label": "License Plate",
				"type": "Data",
				"key": "license_plate",
				"width": "12rem",
			},
			{
				"label": "Make",
				"type": "Data",
				"key": "make",
				"width": "10rem",
			},
			{
				"label": "Model",
				"type": "Data",
				"key": "model",
				"width": "10rem",
			},
			{
				"label": "Fuel Type",
				"type": "Select",
				"key": "fuel_type",
				"width": "8rem",
			},
			{
				"label": "Odometer (Last)",
				"type": "Int",
				"key": "last_odometer",
				"width": "10rem",
			},
			{
				"label": "Vehicle Value",
				"type": "Currency",
				"key": "vehicle_value",
				"width": "10rem",
			},
			{
				"label": "Last Modified",
				"type": "Datetime",
				"key": "modified",
				"width": "8rem",
			},
		]
		rows = [
			"name",
			"license_plate",
			"make",
			"model",
			"fuel_type",
			"last_odometer",
			"vehicle_value",
			"location",
			"modified",
		]
		return {"columns": columns, "rows": rows}