from vanna.ollama import Ollama
from vanna.chromadb import ChromaDB_VectorStore
from vanna.flask import VannaFlaskApp

from vanna.flask.auth import AuthInterface
import flask
import json

class SimplePassword(AuthInterface):
    def __init__(self, users: dict):
        self.users = users

    def get_user(self, flask_request) -> any:
        return flask_request.cookies.get('user')

    def is_logged_in(self, user: any) -> bool:
        return user is not None

    def override_config_for_user(self, user: any, config: dict) -> dict:
        return config

    def login_form(self) -> str:
        return '''
  <div class="p-4 sm:p-7">
    <div class="text-center">
      <h1 class="block text-2xl font-bold text-gray-800 dark:text-white">Sign in To Amaris Analytics</h1>
      <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">

      </p>
    </div>

    <div class="mt-5">

      <!-- Form -->
      <form action="/auth/login" method="POST">
        <div class="grid gap-y-4">
          <!-- Form Group -->
          <div>
            <label for="email" class="block text-sm mb-2 dark:text-white">Email address</label>
            <div class="relative">
              <input type="email" id="email" type="email" name="email" class="py-3 px-4 block w-full border border-gray-200 rounded-lg text-sm focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none dark:bg-slate-900 dark:border-gray-700 dark:text-gray-400 dark:focus:ring-gray-600" required aria-describedby="email-error">
              <div class="hidden absolute inset-y-0 end-0 pointer-events-none pe-3">
                <svg class="size-5 text-red-500" width="16" height="16" fill="currentColor" viewBox="0 0 16 16" aria-hidden="true">
                  <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM8 4a.905.905 0 0 0-.9.995l.35 3.507a.552.552 0 0 0 1.1 0l.35-3.507A.905.905 0 0 0 8 4zm.002 6a1 1 0 1 0 0 2 1 1 0 0 0 0-2z"/>
                </svg>
              </div>
            </div>
            <p class="hidden text-xs text-red-600 mt-2" id="email-error">Please include a valid email address so we can get back to you</p>
          </div>
          <!-- End Form Group -->

          <!-- Form Group -->
          <div>
            <div class="flex justify-between items-center">
              <label for="password" class="block text-sm mb-2 dark:text-white">Password</label>

            </div>
            <div class="relative">
              <input type="password" id="password" name="password" class="py-3 px-4 block w-full border border-gray-200 rounded-lg text-sm focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none dark:bg-slate-900 dark:border-gray-700 dark:text-gray-400 dark:focus:ring-gray-600" required aria-describedby="password-error">
              <div class="hidden absolute inset-y-0 end-0 pointer-events-none pe-3">
                <svg class="size-5 text-red-500" width="16" height="16" fill="currentColor" viewBox="0 0 16 16" aria-hidden="true">
                  <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM8 4a.905.905 0 0 0-.9.995l.35 3.507a.552.552 0 0 0 1.1 0l.35-3.507A.905.905 0 0 0 8 4zm.002 6a1 1 0 1 0 0 2 1 1 0 0 0 0-2z"/>
                </svg>
              </div>
            </div>
            <p class="hidden text-xs text-red-600 mt-2" id="password-error">8+ characters required</p>
          </div>
          <!-- End Form Group -->

          <button type="submit" class="w-full py-3 px-4 inline-flex justify-center items-center gap-x-2 text-sm font-semibold rounded-lg border border-transparent bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 disabled:pointer-events-none">Sign in</button>
        </div>
      </form>
      <!-- End Form -->
    </div>
  </div>
        '''

    def login_handler(self, flask_request) -> str:
        email = flask_request.form['email']
        password = flask_request.form['password']
        # Find the user and password in the users dict
        for user in self.users:
            if user["email"] == email and user["password"] == password:
                response = flask.make_response('Logged in as ' + email)
                response.set_cookie('user', email)
                # Redirect to the main page
                response.headers['Location'] = '/'
                response.status_code = 302
                return response
        else:
            return 'Login failed'

    def callback_handler(self, flask_request) -> str:
        user = flask_request.args['user']
        response = flask.make_response('Logged in as ' + user)
        response.set_cookie('user', user)
        return response

    def logout_handler(self, flask_request) -> str:
        response = flask.make_response('Logged out')
        response.delete_cookie('user')
        return response

def load_config():
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
    return config

class MyVanna(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        Ollama.__init__(self, config=config)

vn = MyVanna(config={'model': 'llama3'})

# Load database configuration from the config file
config = load_config()
db_config = config.get('database', {})

# Extract parameters from the configuration
db_host = db_config.get('db_host', 'localhost')
db_name = db_config.get('db_name', 'ooredoo')
db_user = db_config.get('db_user', 'postgres')
db_password = db_config.get('db_password', 'postgres')
db_port = db_config.get('db_port', '5432')
users = db_config.get('users', [])

vn.connect_to_postgres(host=db_host, dbname=db_name, user=db_user, password=db_password, port=db_port)

ddl = """
CREATE TABLE public.capacities (
    id bigint NOT NULL,
    capacity_value double precision NOT NULL,
    offer_id bigint NOT NULL,
    sector character varying(255) NOT NULL,
    site character varying(255) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE public.catalogs (
    id bigint NOT NULL,
    ooredoo_name character varying(255),
    offer_type character varying(255),
    offer_id bigint NOT NULL,
    ooredoo_id bigint,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    url character varying(255) DEFAULT NULL::character varying
);

CREATE TABLE public.demands (
    id bigint NOT NULL,
    first_name character varying(255),
    last_name character varying(255),
    email character varying(255),
    phone integer,
    address character varying(255),
    postal_code integer,
    town character varying(255),
    comment character varying(500),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE public.endpoint_usage_tracking (
    id uuid NOT NULL,
    ip_address character varying(255) NOT NULL,
    endpoint character varying(255) NOT NULL,
    response_status character varying(255) NOT NULL,
    response_body text NOT NULL,
    requested_at timestamp without time zone DEFAULT now() NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE public.flyway_schema_history (
    installed_rank integer NOT NULL,
    version character varying(50),
    description character varying(200) NOT NULL,
    type character varying(20) NOT NULL,
    script character varying(1000) NOT NULL,
    checksum integer,
    installed_by character varying(100) NOT NULL,
    installed_on timestamp without time zone DEFAULT now() NOT NULL,
    execution_time integer NOT NULL,
    success boolean NOT NULL
);

CREATE TABLE public.history_imports (
    id bigint NOT NULL,
    name character varying(255) NOT NULL,
    status character varying(255),
    imported_at timestamp without time zone DEFAULT now(),
    completed_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    is_excel_file boolean
);

CREATE TABLE public.oauth2_authorization (
    id character varying(100) NOT NULL,
    registered_client_id character varying(100) NOT NULL,
    principal_name character varying(200) NOT NULL,
    authorization_grant_type character varying(100) NOT NULL,
    authorized_scopes character varying(1000) DEFAULT NULL::character varying,
    attributes text,
    state character varying(500) DEFAULT NULL::character varying,
    authorization_code_value text,
    authorization_code_issued_at timestamp without time zone,
    authorization_code_expires_at timestamp without time zone,
    authorization_code_metadata text,
    access_token_value text,
    access_token_issued_at timestamp without time zone,
    access_token_expires_at timestamp without time zone,
    access_token_metadata text,
    access_token_type character varying(100) DEFAULT NULL::character varying,
    access_token_scopes character varying(1000) DEFAULT NULL::character varying,
    oidc_id_token_value text,
    oidc_id_token_issued_at timestamp without time zone,
    oidc_id_token_expires_at timestamp without time zone,
    oidc_id_token_metadata text,
    refresh_token_value text,
    refresh_token_issued_at timestamp without time zone,
    refresh_token_expires_at timestamp without time zone,
    refresh_token_metadata text,
    user_code_value text,
    user_code_issued_at timestamp without time zone,
    user_code_expires_at timestamp without time zone,
    user_code_metadata text,
    device_code_value text,
    device_code_issued_at timestamp without time zone,
    device_code_expires_at timestamp without time zone,
    device_code_metadata text
);

CREATE TABLE public.oauth2_registered_client (
    id uuid NOT NULL,
    authorization_grant_types character varying(1000) NOT NULL,
    client_authentication_methods character varying(1000) NOT NULL,
    client_id character varying(255) NOT NULL,
    client_id_issued_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    client_name character varying(255) NOT NULL,
    client_secret character varying(255),
    client_secret_expires_at timestamp without time zone,
    client_settings character varying(2000) NOT NULL,
    post_logout_redirect_uris character varying(1000),
    redirect_uris character varying(1000),
    scopes character varying(1000) NOT NULL,
    token_settings character varying(2000) NOT NULL
);

CREATE TABLE public.offers (
    id bigint NOT NULL,
    legend character varying(255) NOT NULL,
    public_id character varying(255),
    technology_id bigint NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE public.rapports (
    id bigint NOT NULL,
    first_name character varying(255),
    last_name character varying(255),
    email character varying(255),
    phone integer,
    address character varying(255),
    point character varying(255),
    ooredoo_id integer,
    ooredoo_name character varying(255),
    application_name character varying(255),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE public.shapes (
    id bigint NOT NULL,
    priority boolean DEFAULT false,
    legend character varying(255),
    name character varying(255),
    offer_id bigint NOT NULL,
    the_geom public.geometry,
    sales_authorization boolean DEFAULT true,
    sla integer,
    item_type character varying(255),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE public.technologies (
    id bigint NOT NULL,
    legend character varying(255) NOT NULL,
    public_id character varying(255),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE public.uploaded_files (
    id bigint NOT NULL,
    file_name character varying(255) NOT NULL,
    uplaoded boolean,
    uploaded_at character varying(255),
    archived boolean,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    status character varying(255),
    history_import_id bigint NOT NULL
);

"""
vn.train(ddl=ddl)
training_data = vn.get_training_data()
training_data

app = VannaFlaskApp(
    vn=vn,
    auth=SimplePassword(users=users),
    logo="https://amaris.com/wp-content/uploads//2020/08/amaris-logo-blue.svg",
    title="Welcome to Amaris AI Analytics",
    subtitle="Your AI-powered copilot for charts and sql.",
)
app.run()