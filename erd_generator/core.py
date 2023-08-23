from sqlalchemy import create_engine, MetaData, Table
from graphviz import Digraph


def load_metadata(database_url, schema_name, tables_to_include):
    """
    Load metadata from the database.

    :param database_url: Connection URL for the database.
    :param schema_name: Specific schema name within the database.
    :param tables_to_include: List of table names to include; includes all if None.
    :return: SQLAlchemy MetaData object.
    """
    engine = create_engine(database_url)
    metadata = MetaData(schema=schema_name)

    with engine.connect() as connection:
        if tables_to_include:
            [Table(name, metadata, autoload_with=connection, schema=schema_name) for name in tables_to_include]
        else:
            metadata.reflect(bind=connection, schema=schema_name)

    return metadata

def render_column(column):
    """
    Generate HTML representation for a single table column.

    :param column: SQLAlchemy Column object.
    :return: HTML string for the column.
    """
    return f'<tr><td border="1" cellpadding="4">{column.name}</td><td border="1" cellpadding="4">{column.type}</td></tr>'

def render_relationship(column, processed_relationships, erd):
    """
    Render relationships for a given column, including foreign keys.

    :param column: SQLAlchemy Column object containing foreign keys.
    :param processed_relationships: Set of relationships that have been processed.
    :param erd: Graphviz object representing the ERD.
    """
    for fk in column.foreign_keys:
        referenced_table = fk.column.table.name
        
        relationship = (column.table.name, referenced_table, column.name, fk.column.name)

        if relationship not in processed_relationships:
            processed_relationships.add(relationship)
            
            edge_label = f"{column.name} ⟶ {fk.column.name}"

            erd.node(edge_label, label=edge_label, shape='plaintext', fontsize='10', fontcolor='blue', width='0', height='0')
            erd.edge(column.table.name, edge_label, arrowhead='none', constraint='true')
            erd.edge(edge_label, referenced_table, constraint='true')

def render_table(table, erd):
    """
    Render an entire table, including its columns.

    :param table: SQLAlchemy Table object.
    :param erd: Graphviz object representing the ERD.
    """
    rows = [render_column(column) for column in table.columns]
    
    table_html = f'<<table border="1" cellspacing="0" cellpadding="4"><tr><td bgcolor="lightblue" colspan="2" border="1">{table.name}</td></tr>' + ''.join(rows) + '</table>>'
    
    erd.node(table.name, label=table_html, shape='plaintext')

def generate_erd(database_url, schema_name, tables_to_include):
    """
    Generate an Entity-Relationship Diagram (ERD) for the specified database.

    :param database_url: Connection URL for the database.
    :param schema_name: Specific schema name within the database.
    :param tables_to_include: List of table names to include in the ERD; includes all if None.
    """
    try:
        metadata = load_metadata(database_url, schema_name, tables_to_include)
        
        erd = Digraph(name='ERD', filename='ERD', format='png', node_attr={'margin': '0'})

        processed_relationships = set()

        for table in metadata.sorted_tables:
            render_table(table, erd)
            
            for column in table.columns:
                render_relationship(column, processed_relationships, erd)

        erd.view()

    except Exception as e:
        print(f"Error generating ERD: {e}")
