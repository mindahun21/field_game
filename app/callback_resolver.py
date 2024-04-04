


router = dict(

)

def resolver(data_type:str):
    return router.get(data_type)