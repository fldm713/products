"""
My Service

Describe what your service does here
"""

import os
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort


# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from service.models import Product, DataValidationError
from werkzeug.exceptions import NotFound
# Import Flask application
from service import app, status  # HTTP Status Codes
# app.config["APPLICATION_ROOT"] = "/api"

######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return (
         jsonify(
            name="Product Demo REST API Service",
            version="1.0",
        ),
        status.HTTP_200_OK,
    )

######################################################################
# UPDATE AN EXISTING PRODUCT
######################################################################
@app.route("/products/<int:product_id>", methods=["PUT"])
def update_products(product_id):
    """
    Update a Product
    This endpoint will update a Product based the body that is posted
    """
    app.logger.info("Request to update Product with id %s", product_id)
    check_content_type("application/json")
    product = Product.find(product_id)
    if not product:
        raise NotFound("Product with id %d was not found." % product_id)

    product.deserialize(request.get_json())
    product.update()
    app.logger.info("Product with id [%d] updated.", product.id)
    return make_response(jsonify(product.serialize()), status.HTTP_200_OK)


######################################################################
# DELETE A PRODUCT
######################################################################
@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_products(product_id):
    """
    Delete a Product
    This endpoint will delete a Product based the id specified in the path
    """
    app.logger.info("Request to delete Product with id %s", product_id)
    product = Product.find(product_id)
    if product:
        product.delete()
    app.logger.info("Product with id [%s] delete", product_id)
    return make_response(jsonify(message = ''), status.HTTP_204_NO_CONTENT)

# #####################################################################
# PURCHASE A product
# #####################################################################
@app.route("/products/<int:product_id>/purchase", methods=["PUT"])
def purchase_products(product_id):
    """Purchase a product"""
    app.logger.info("Request to purchase product with id %s", product_id)
    check_content_type("application/json")
    product = Product.find(product_id)
    if not product:
        abort(
            status.HTTP_404_NOT_FOUND, "product with id '{}' was not found.".format(product_id)
        )
    return make_response(jsonify(product.serialize()), status.HTTP_200_OK)

@app.route("/products", methods=["GET"])
def list_product():
    """ Returns all of the products """
    app.logger.info("Request for product list")
    products = []
    products = Product.all()

    results = [product.serialize() for product in products]
    return make_response(jsonify(results), status.HTTP_200_OK)

######################################################################
# RETRIEVE A product
######################################################################
@app.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    """
    Retrieve a single product

    This endpoint will return a product based on it's id
    """
    app.logger.info("Request for product with id: %s", product_id)
    product = Product.find(product_id)
    if not product:
        raise NotFound("product with id '{}' was not found.".format(product_id))
    return product.serialize(), status.HTTP_200_OK

######################################################################
# ADD A NEW product
######################################################################
@app.route("/products", methods=["POST"])
def create_product():
    """
    Creates a product
    This endpoint will create a product based the data in the body that is posted
    """
    app.logger.info("Request to create a product")
    check_content_type("application/json")
    product = Product()
    product.deserialize(request.get_json())
    product.create()
    message = product.serialize()
    location_url = url_for("get_product", product_id=product.id, _external=True)
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
# @app.before_first_request
def initialize_logging(log_level=logging.INFO):
    """Initialized the default logging to STDOUT"""
    if not app.debug:
        print("Setting up logging...")
        # Set up default logging for submodules to use STDOUT
        # datefmt='%m/%d/%Y %I:%M:%S %p'
        fmt = "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
        logging.basicConfig(stream=sys.stdout, level=log_level, format=fmt)
        # Make a new log handler that uses STDOUT
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(fmt))
        handler.setLevel(log_level)
        # Remove the Flask default handlers and use our own
        handler_list = list(app.logger.handlers)
        for log_handler in handler_list:
            app.logger.removeHandler(log_handler)
        app.logger.addHandler(handler)
        app.logger.setLevel(log_level)
        app.logger.propagate = False
        app.logger.info("Logging handler established")

def init_db():
    """ Initializes the SQLAlchemy app """
    global app
    Product.init_db(app)

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers["Content-Type"] == content_type:
        return
    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(415, "Content-Type must be {}".format(content_type))