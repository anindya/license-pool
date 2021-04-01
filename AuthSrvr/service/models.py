# Code adapted from John J. Rofrano's [nyu-devops/lab-flask-tdd]:
# https://github.com/nyu-devops/lab-flask-tdd

"""
Models for the Authorizing Service

All of the models are stored in this module

Models
------
User - a registered user
    Attributes:
    -----------
    uname (string) - the username
    password (string) - the hashed password

License_Permit - a record of the number of license allowed and the number of license in use for each user
    Attributes:
    -----------
    uname (string) - the username
    max_licenses (integer) 
        - the number of license allowed for this user
    in_use (integer) 
        - the number of license currently in use for this user

License - a license
    Attributes:
    -----------
    uname (string) - the username
    public_key (text) 
        - plain text of the public_key
    private_key (text) 
        - plain text of the public_key
    in_use (boolean) 
        - True for license that's in use by any container
    container_id (string) 
        - the container_id of the container that's currently using the license
    last_used (datetime) 
        - datetime when a license was last assigned to a container
"""

import logging
from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """

    pass


class User(db.Model):
    """
    Class that represents a User
    """
    __tablename__ = 'users'
    logger = logging.getLogger(__name__)
    app = None

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    uname = db.Column(db.String(64), unique=True, index=True)  # TODO: need to confirm the data type
    password = db.Column(db.String(128))  # TODO: need to confirm the data type
    permit = db.relationship('License_Permit', backref='user', uselist=False)
    licenses = db.relationship('License', backref='user')

    ##################################################
    # INSTANCE METHODS
    ##################################################
    # def __init__(self, uname, password):
    #     self.uname = uname
    #     self.password = password

    def __repr__(self):
        return "<User %r>" % (self.id)

    def create(self):
        """
        Creates a User to the data store
        """
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a User to the data store
        """
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        db.session.commit()

    def delete(self):
        """ Removes a User from the data store """
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a User into a dictionary """
        return {
            "id": self.id,
            "uname": self.uname,
            "password": self.password,
        }

    def deserialize(self, data: dict):
        """
        Deserializes a User from a dictionary

        :param data: a dictionary of attributes
        :type data: dict

        :return: a reference to self
        :rtype: User

        """
        try:
            self.logger.debug(data)
            self.uname = data["uname"]
            self.password = data["password"]
        except KeyError as error:
            raise DataValidationError("Invalid User: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid User: body of request contained bad or no data"
            )
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """ Returns all of the Users in the database """
        cls.logger.info("Processing all Users")
        return cls.query.all()

    @classmethod
    def find(cls, user_id: int):
        """Finds a User by it's ID

        :param user_id: the id of the User to find
        :type user_id: int

        :return: an instance with the user_id, or None if not found
        :rtype: User

        """
        cls.logger.info("Processing lookup for id %s ...", user_id)
        return cls.query.get(user_id)

    @classmethod
    def find_by_uname(cls, uname):
        cls.logger.info(f"Processing lookup for uname {uname} ...")
        return cls.query.filter_by(uname=uname).first()

    @classmethod
    def find_or_404(cls, user_id: int):
        """Find a User by it's id

        :param user_id: the id of the User to find
        :type user_id: int

        :return: an instance with the user_id, or 404_NOT_FOUND if not found
        :rtype: User

        """
        cls.logger.info("Processing lookup or 404 for id %s ...", user_id)
        return cls.query.get_or_404(user_id)


class License_Permit(db.Model):
    """
    Class that represents a License_Permit
    """
    __tablename__ = "license_permits"
    logger = logging.getLogger(__name__)
    app = None

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    max_licenses = db.Column(db.Integer)
    in_use = db.Column(db.Integer)

    ##################################################
    # INSTANCE METHODS
    ##################################################

    def __repr__(self):
        return "<License_Permit %r>" % (self.id)

    def create(self):
        """
        Creates a License_Permit to the data store
        """
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a License_Permit to the data store
        """
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        db.session.commit()

    def delete(self):
        """ Removes a License_Permit from the data store """
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a License_Permit into a dictionary """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "max_licenses": self.max_licenses,
            "in_use": self.in_use,
        }

    def deserialize(self, data: dict):
        """
        Deserializes a License_Permit from a dictionary

        :param data: a dictionary of attributes
        :type data: dict

        :return: a reference to self
        :rtype: License_Permit

        """
        try:
            self.user_id = data["user_id"]
            self.max_licenses = data["max_licenses"]
            self.in_use = data["in_use"]
        except KeyError as error:
            raise DataValidationError("Invalid License: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid License: body of request contained bad or no data"
            )
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """ Returns all of the License_Permit in the database """
        cls.logger.info("Processing all License_Permit")
        return cls.query.all()

    @classmethod
    def find(cls, license_permit_id: int):
        """Finds a License_Permit by it's ID

        :param license_permit_id: the id of the License_Permit to find
        :type license_permit_id: int

        :return: an instance with the license_permit_id, or None if not found
        :rtype: License_Permit

        """
        cls.logger.info("Processing lookup for id %s ...", license_permit_id)
        return cls.query.get(license_permit_id)

    @classmethod
    def find_by_uid(cls, uid):
        return cls.query.filter_by(user_id=uid).first()

    @classmethod
    def find_or_404(cls, license_permit_id: int):
        """Find a License_Permit by it's id

        :param license_permit_id: the id of the License_Permit to find
        :type license_permit_id: int

        :return: an instance with the license_permit_id, or 404_NOT_FOUND if not found
        :rtype: License_Permit

        """
        cls.logger.info("Processing lookup or 404 for id %s ...", license_permit_id)
        return cls.query.get_or_404(license_permit_id)


class License(db.Model):
    """
    Class that represents a License

    This version uses a relational database for persistence which is hidden
    from us by SQLAlchemy's object relational mappings (ORM)
    """
    __tablename__ = "licenses"
    logger = logging.getLogger(__name__)
    app = None

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    public_key = db.Column(db.Text(), index=True)
    private_key = db.Column(db.Text())
    in_use = db.Column(db.Boolean(), index=True)
    container_id = db.Column(db.String(64))
    last_used = db.Column(db.DateTime())

    ##################################################
    # INSTANCE METHODS
    ##################################################

    def __repr__(self):
        return "<License %r>" % (self.id)

    def create(self):
        """
        Creates a License to the data store
        """
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a License to the data store
        """
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        db.session.commit()

    def delete(self):
        """ Removes a License from the data store """
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a License into a dictionary """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "public_key": self.public_key,
            "private_key": self.private_key,
            "in_use": self.in_use,
            "container_id": self.container_id,
            "last_used": self.last_used,
        }

    def deserialize(self, data: dict):
        """
        Deserializes a License from a dictionary

        :param data: a dictionary of attributes
        :type data: dict

        :return: a reference to self
        :rtype: License

        """
        try:
            self.user_id = data["user_id"]
            self.public_key = data["public_key"]
            self.private_key = data["private_key"]
            self.in_use = data["in_use"]
            self.container_id = data["container_id"]
            self.last_used = data["last_used"]
        except KeyError as error:
            raise DataValidationError("Invalid License: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid License: body of request contained bad or no data"
            )
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def init_db(cls, app):
        """Initializes the database session

        :param app: the Flask app
        :type data: Flask

        """
        cls.logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.drop_all()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the Licenses in the database """
        cls.logger.info("Processing all Licenses")
        return cls.query.all()

    @classmethod
    def find(cls, license_id: int):
        """Finds a License by it's ID

        :param license_id: the id of the License to find
        :type license_id: int

        :return: an instance with the license_id, or None if not found
        :rtype: License

        """
        cls.logger.info("Processing lookup for id %s ...", license_id)
        return cls.query.get(license_id)

    @classmethod
    def find_by_uid(cls, uid):
        return cls.query.filter_by(user_id=uid).all()

    @classmethod
    def find_free_by_uid(cls, uid):
        return cls.query.filter_by(user_id=uid, in_use=False).first()

    @classmethod
    def find_by_uid_container_id(cls, user_id, container_id):
        return cls.query.filter_by(user_id=user_id, container_id=container_id).first()
    @classmethod
    def find_or_404(cls, license_id: int):
        """Find a License by it's id

        :param license_id: the id of the License to find
        :type license_id: int

        :return: an instance with the license_id, or 404_NOT_FOUND if not found
        :rtype: License

        """
        cls.logger.info("Processing lookup or 404 for id %s ...", license_id)
        return cls.query.get_or_404(license_id)

    # @classmethod
    # def find_by_name(cls, name: str):
    #     """Returns all Pets with the given name

    #     :param name: the name of the Pets you want to match
    #     :type name: str

    #     :return: a collection of Pets with that name
    #     :rtype: list

    #     """
    #     cls.logger.info("Processing name query for %s ...", name)
    #     return cls.query.filter(cls.name == name)

    # @classmethod
    # def find_by_category(cls, category: str):
    #     """Returns all of the Pets in a category

    #     :param category: the category of the Pets you want to match
    #     :type category: str

    #     :return: a collection of Pets in that category
    #     :rtype: list

    #     """
    #     cls.logger.info("Processing category query for %s ...", category)
    #     return cls.query.filter(cls.category == category)

    # @classmethod
    # def find_by_availability(cls, available: bool = True):
    #     """Returns all Pets by their availability

    #     :param available: True for pets that are available
    #     :type available: str

    #     :return: a collection of Pets that are available
    #     :rtype: list

    #     """
    #     cls.logger.info("Processing available query for %s ...", available)
    #     return cls.query.filter(cls.available == available)
