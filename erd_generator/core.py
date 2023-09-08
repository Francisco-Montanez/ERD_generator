import os, logging
from sqlalchemy import create_engine, MetaData, Table
from graphviz import Digraph

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
        tables = tables_to_include or metadata.reflect(bind=connection, schema=schema_name).tables.keys()

        [Table(name, metadata, autoload_with=connection, schema=schema_name) for name in tables]

    return metadata

def render_column(column):
    """
    Generate HTML representation for a single table column.

    :param column: SQLAlchemy Column object.
    :return: HTML string for the column.
    """
    column_type = 'PK' if column.primary_key else 'FK' if column.foreign_keys else ''

    return f'<tr><td>{column.name}</td><td>{column.type}</td><td>{column_type}</td></tr>'

def render_relationship(column, processed_relationships, erd):
    """
    Render relationships for a given column, including foreign keys.

    :param column: SQLAlchemy Column object containing foreign keys.
    :param processed_relationships: Set of relationships that have been processed.
    :param erd: Graphviz object representing the ERD.
    """
    for fk in column.foreign_keys:
        relationship = (column.table.name, fk.column.table.name, column.name, fk.column.name)

        if relationship not in processed_relationships:
            processed_relationships.add(relationship)

            edge_label = f"[{relationship[0]}.{relationship[2]}] references [{relationship[1]}.{relationship[3]}]"

            erd.edge(relationship[0], relationship[1], label=edge_label, fontsize='10', fontcolor='blue')

def render_table(table, erd):
    """
    Render an entire table, including its columns.

    :param table: SQLAlchemy Table object.
    :param erd: Graphviz object representing the ERD.
    """
    rows = ''.join(map(render_column, table.columns))
    
    table_html = f'<<table><tr><td bgcolor="lightblue" colspan="3">{table.name}</td></tr>{rows}</table>>'

    erd.node(table.name, label=table_html, shape='plaintext')

def generate_erd(database_url, schema_name, tables_to_include, output_directory, cleanup):
    """
    Generate an Entity-Relationship Diagram (ERD) for the specified database.

    :param database_url: Connection URL for the database.
    :param schema_name: Specific schema name within the database.
    :param tables_to_include: List of table names to include in the ERD; includes all if None.
    :param output_directory: Directory to save the ERD.
    :param cleanup: Whether to clean up the generated dot file.
    """
    try:
        metadata = load_metadata(database_url, schema_name, tables_to_include)
        
        erd = Digraph(name='ERD', filename=f'{output_directory}/ERD', format='png', node_attr={'margin': '0'})

        processed_relationships = set()

        for table in metadata.sorted_tables:
            render_table(table, erd)
        
            list(map(lambda column: render_relationship(column, processed_relationships, erd), table.columns))

        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        erd.render(f"{output_directory}/ERD", cleanup=cleanup)

    except Exception as e:
        logging.error(f"Error generating ERD: {e}")
