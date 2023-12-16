import json

from flask import Flask, request, render_template, jsonify, redirect, url_for

app = Flask(__name__, static_url_path='/static')

# Load the initial configuration from config.json
with open('config.json', 'r') as config_file:
    config_data = json.load(config_file)


# Define a route for the root URL ("/")
@app.route('/')
def index():
    # Render the index.html template and pass the config data to it
    return render_template('index.html', config=config_data)


@app.route('/pages/commands')
def commands():
    return render_template('pages/commands.html')


@app.route('/pages/about')
def about():
    return render_template('pages/about.html')


# Define a route for the Bot Configuration page
@app.route('/config')
def config_page():
    # Pass the config_data dictionary to the template
    return render_template('config.html', config=config_data)


# Add separate routes for updating each configuration value

@app.route('/set_config', methods=['POST'])
def set_config():
    new_token = request.form.get('token')
    new_prefix = request.form.get('prefix')
    new_welcome_message = request.form.get('welcome_message')
    new_dingo_description = request.form.get('dingo_description')

    # Update the config_data dictionary with the new values
    if new_token is not None:
        config_data['token'] = new_token
    if new_prefix is not None:
        config_data['prefix'] = new_prefix
    if new_welcome_message is not None:
        config_data['welcome_message'] = new_welcome_message
    if new_dingo_description is not None:
        config_data['dingo_description'] = new_dingo_description

    # Save the updated configuration back to config.json
    with open('config.json', 'w') as config_file:
        json.dump(config_data, config_file, indent=4)

    # Return a JSON response to indicate success
    response = {'message': 'Configuration edited correctly'}
    return jsonify(response)


# Create separate routes for updating specific configuration values
@app.route('/set_token', methods=['POST'])
def set_token():
    new_token = request.form.get('token')
    # Update the token in your config_data
    if new_token is not None:
        config_data['token'] = new_token
        # Save the updated configuration back to config.json if needed
        with open('config.json', 'w') as config_file:
            json.dump(config_data, config_file, indent=4)
        # Return a JSON response indicating success
        response = {'message': 'Bot Token edited correctly'}
        return jsonify(response)


@app.route('/set_prefix', methods=['POST'])
def set_prefix():
    new_prefix = request.form.get('prefix')

    # Update the prefix in your config_data
    config_data['prefix'] = new_prefix

    # Save the updated configuration back to config.json
    with open('config.json', 'w') as config_file:
        json.dump(config_data, config_file, indent=4)

    # Return a JSON response indicating success
    response = {'message': 'Prefix edited correctly'}
    return jsonify(response)


@app.route('/set_dingo_description', methods=['POST'])
def set_dingo_description():
    new_dingo_description = request.form.get('dingo_description')

    # Update the dingo_description in your config_data
    config_data['dingo_description'] = new_dingo_description

    # Save the updated configuration back to config.json
    with open('config.json', 'w') as config_file:
        json.dump(config_data, config_file, indent=4)

    # Return a JSON response indicating success
    response = {'message': 'Dingo Description edited correctly'}
    return jsonify(response)


@app.route('/set_welcome_message', methods=['POST'])
def set_welcome_message():
    new_welcome_message = request.form.get('welcome_message')
    # Update the welcome_message in your config_data
    if new_welcome_message is not None:
        config_data['welcome_message'] = new_welcome_message
        # Save the updated configuration back to config.json if needed
        with open('config.json', 'w') as config_file:
            json.dump(config_data, config_file, indent=4)
        # Return a JSON response indicating success
        response = {'message': 'Welcome Message edited correctly'}
        return jsonify(response)


# Define a route for updating throw_items
@app.route('/update_throw_items', methods=['POST'])
def update_throw_items():
    new_item = request.form.get('new_item')
    if new_item:
        # Append the new item to the throw_items list in your throw_items.json
        with open('throw_items.json', 'r') as throw_items_file:
            throw_items_data = json.load(throw_items_file)
            throw_items_data['items'].append(new_item)

        # Save the updated throw_items list back to throw_items.json
        with open('throw_items.json', 'w') as throw_items_file:
            json.dump(throw_items_data, throw_items_file, indent=4)

    # Redirect back to the page with the updated list
    return redirect(url_for('index'))


# Define a route for the /throw_items page
@app.route('/throw_items')
def throw_items():
    # Load the throw_items list from throw_items.json
    with open('throw_items.json', 'r') as throw_items_file:
        throw_items_data = json.load(throw_items_file)
    # Render the throw_items.html template and pass the throw_items list to it
    return render_template('throw_items.html', throw_items=throw_items_data['items'])


# Ensure this is the last line in your Flask application
if __name__ == '__main__':
    app.run(debug=True)
