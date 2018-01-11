from eve import Eve

app = Eve()

def use_collection('20180110_140045'):
    app.config['DOMAIN'] =  {'20180110_140045': {}}
    domain_copy = copy.deepcopy(app.config['DOMAIN'])
    for resource, settings in domain_.items():
        app.register_resource(resource, settings)

# allowed_filters = ['base_url']
# additional_lookup

if __name__ == '__main__':
    app.run()
