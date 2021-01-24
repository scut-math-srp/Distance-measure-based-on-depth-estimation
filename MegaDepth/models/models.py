
def create_model(opt, parameters):
    model = None
    from .HG_model import hgmodel
    model = hgmodel(opt, parameters)
    print("model [%s] was created" % (model.name()))
    return model
