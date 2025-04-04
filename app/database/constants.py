from typing import Final

POSTGRES_INDEXES_NAMING_CONVENTION: Final[dict[str, str]] = {
    'ix': '%(column_0_label)s_idx',
    'uq': '%(table_name)s_%(column_0_name)s_key',
    'ck': '%(table_name)s_%(constraint_name)s_check',
    'fk': '%(table_name)s_%(column_0_name)s_%(referred_table_name)s_fkey',
    'pk': '%(table_name)s_pkey',
}
