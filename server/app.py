#!/usr/bin/env python3

from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Newsletter

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newsletters.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)
db.init_app(app)

ma = Marshmallow(app)

class NewsletterSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = Newsletter
        load_instance = True

    url = ma.Hyperlinks(
        {
            "self": ma.URLFor(
                "newsletterbyid",
                values=dict(id="<id>")),
            "collection": ma.URLFor("newsletters"),
        }
    )

newsletter_schema = NewsletterSchema()
newsletters_schema = NewsletterSchema(many=True)

api = Api(app)

class Index(Resource):

    def get(self):

        response_dict = {
            "index": "Welcome to the Newsletter RESTful API",
        }

        return jsonify(response_dict)

api.add_resource(Index, '/')

class Newsletters(Resource):

    def get(self):

        newsletters = Newsletter.query.all()

        return newsletters_schema.dump(newsletters)

    def post(self):

        new_newsletter = Newsletter(
            title=request.form.get('title'),
            body=request.form.get('body'),
        )

        db.session.add(new_newsletter)
        db.session.commit()

        return newsletter_schema.dump(new_newsletter), 201

api.add_resource(Newsletters, '/newsletters')

class NewsletterByID(Resource):

    def get(self, id):

        newsletter = Newsletter.query.get(id)

        if not newsletter:
            return {'message': 'Newsletter not found'}, 404

        return newsletter_schema.dump(newsletter)

    def patch(self, id):

        newsletter = Newsletter.query.get(id)

        if not newsletter:
            return {'message': 'Newsletter not found'}, 404

        for attr, value in request.form.items():
            setattr(newsletter, attr, value)

        db.session.commit()

        return newsletter_schema.dump(newsletter)

    def delete(self, id):

        newsletter = Newsletter.query.get(id)

        if not newsletter:
            return {'message': 'Newsletter not found'}, 404

        db.session.delete(newsletter)
        db.session.commit()

        return {'message': 'Newsletter deleted successfully'}, 200

api.add_resource(NewsletterByID, '/newsletters/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
