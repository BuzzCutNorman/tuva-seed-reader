# Tuva Seed Reader #
This little application is to be used in conjunction with The Tuva Project DBT package when utilizing PostgesSQL for you datawarehouse.  The Tuva Seed Reader allows you to override the load_seed macro with a PostgreSQL version that leverages COPY FROM PROGRAM.  You guessed it the program that you are copying the data from is the Tuva Seed Reader.  The same URI and PATTERN argumanets passed in the post-hook calls found in The Tuva Project dbt_project.yml file.

## How Get it Working ##
You need to complete two task in order to get the Tuva Seed Reader and working with the Tuva data project.

1) Install the tuva seed reader on you PostgresSQL server.
2) Override the load_macro macro in your DBT Project.

## Installing Tuva Seed Reader ##
Windows does not have a global installtion for pipx so you need to run the PostgreSQL service under a local or domain account.  When you connect you will need to connect at this service users so you can complete the following steps.

Connect to your PostgreSQL Server and complete these steps:

1. [Install python 3.9 or greater](https://www.python.org/downloads/). (I tested mainly with 3.12)
2. Connect to the server as the service user.
3. [Install pipx](https://pipx.pypa.io/latest/installation/).
    ```bash
    py -m pip install --user pipx
    ```
4. Ensure pipx path.
    ```bash
    pipx ensurepath
    ```
5. Install tuva seed reader.
    ```bash
    pipx install https://github.com/BuzzCutNorman/tuva-seed-reader/archive/refs/heads/main.zip
    ```
6. Test you can run the Tuva Seed Reader
    ```bash
    tuva-seed-reader
    ```

## Override the `load_seed` Macro ##
In your DBT project folder open your dbt_project.yml and andd the below dispatch: .  Change the placeholder 'your_project_name_here' to you project's macro name space.  If you do not have, one use the name of your project.  That is what I did and it seems to work nicely.

```
dispatch:
  - macro_namespace: the_tuva_project
    search_order: ['your_project_name_here','the_tuva_project']
```

In your DBT project folder, create a macros forlder if you do not already have one.  In that folder create a new file and name it `load_seed.sql`.  Cut and paste in the below code and save the file.

```
{% macro postgres__load_seed(uri,pattern,compression,headers,null_marker) %}

{% set sql %}
COPY {{ this }}
  FROM PROGRAM 'tuva-seed-reader {{ uri }} {{ pattern }}'
  WITH (FORMAT CSV{% if headers == True %}, HEADER MATCH{% endif %})
{% endset %}

{% if execute %}
{# debugging { log(sql, True)} #}
{% set results = run_query(sql) %}
{{ log("Loaded data from external s3 resource\n  loaded to: " ~ this ~ "\n  from: s3://" ~ uri ,True) }}
{# debugging { log(results, True) } #}
{% endif %}

{% endmacro %}
```

### Testing ###
I would suggest running `dbt seed` or `dbt build`.  Hopefully you will see all the terminology, reference, and valueset data get seeded properly.  If you have, a failure and you want to see more in the logs you can add `--log-level debug` to the dbt command you used.
