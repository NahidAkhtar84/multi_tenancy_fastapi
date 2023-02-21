from typing import Any
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import as_declarative, declared_attr, declarative_base


metadata = MetaData()
Base = declarative_base(metadata=metadata)


def get_shared_metadata():
    meta = MetaData()
    for table in Base.metadata.tables.values():
        if table.schema != "tenant":
            table.tometadata(meta)
    return meta

def get_tenant_specific_metadata():
    meta = MetaData(schema="tenant")
    for table in Base.metadata.tables.values():
        if table.schema == "tenant":
            table.tometadata(meta)
    return meta