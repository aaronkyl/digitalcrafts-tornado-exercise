import tornado.ioloop
import tornado.web
import os
import boto3

from jinja2 import Environment, PackageLoader, select_autoescape
  
ENV = Environment(
    loader=PackageLoader('myapp', 'templates'),
    autoescape=select_autoescape(['html', 'xml']))

client = boto3.client(
  'ses',
  aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
  aws_secret_access_key=os.environ.get('AWS_SECRET_KEY'),
  region_name='us-east-1'
)
    
class TemplateHandler(tornado.web.RequestHandler):
    def render_template (self, tpl, context):
        template = ENV.get_template(tpl)
        self.write(template.render(**context))

class MainHandler(TemplateHandler):
    def get(self):
        self.render_template("home.html", {})
        
class TestHandler(TemplateHandler):
    def get(self):
        self.render_template("test.html", {})
        
class RecipeHandler(TemplateHandler):
    def get(self):
        self.render_template("recipes.html", {})
        
class AboutHandler(TemplateHandler):
    def get(self):
        self.render_template("about.html", {})
        
class ContactHandler(TemplateHandler):
    def get(self):
        self.render_template("contact.html", {})
        
    def post(self):
        # form_data = self.request.arguments
        email = self.get_body_argument('email')
        sender_name = self.get_body_argument('firstname') + ' ' + self.get_body_argument('lastname')
        message = self.get_body_argument('message')
        
        send_email(sender_name, email, message)
        
        self.render_template("contact.html", {'message': "Thank you for contacting us!"})

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/test", TestHandler),
        (r"/recipes", RecipeHandler),
        (r"/about", AboutHandler),
        (r"/contact", ContactHandler),
        (
            r"/static/(.*)",
            tornado.web.StaticFileHandler,
            {'path': 'static'}
        ),
        ], autoreload=True)

def send_email(sender_name, sender_email, message):
    client.send_email(
        Destination={
            'ToAddresses': ['aaronwilkinson@gmail.com'],
        },
        Message={
            'Body': {
                'Text': {
                    'Charset': 'UTF-8',
                    'Data': "{} at {} says: \n\n{}".format(sender_name, sender_email, message),
                },
            },
            'Subject': {'Charset': 'UTF-8', 'Data': 'The Joys of Cooking - Contact Message'},
        },
        Source='aaronwilkinson@gmail.com',
    )

if __name__ == "__main__":
    tornado.log.enable_pretty_logging()

    app = make_app()
    PORT = int(os.environ.get('PORT', '8080'))
    app.listen(PORT)
    tornado.ioloop.IOLoop.current().start()