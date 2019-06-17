from typing import List


class DependencyRecord:
    def __init__(self, own_table:str = '', ref_key:str = '', ref_table:str = '', ref_table_pk:str = ''):
        self.own_table = own_table
        self.ref_table = ref_table
        self.ref_key = ref_key
        self.ref_table_pk = ref_table_pk

    def __repr__(self):
        return f'{self.own_table}.{self.ref_key} -> {self.ref_table}.{self.ref_table_pk}'


class TableDeps:
    """
    Class represents table dependencies chain, build on foreign key references
    Used in bulk delete procedure
    """
    def __init__(self, start_dep):
        self.own_table_pk = []  #type:List[str]
        if start_dep:
            self.own_table_pk = start_dep.own_table_pk
            self.deps = start_dep.deps[:]
            return
        self.deps = []  # type: List[DependencyRecord]

    def __repr__(self) -> str:
        pk_str = ','.join(self.own_table_pk)
        return f'pk:[{pk_str}], ' + ', '.join([str(d) for d in self.deps])

    @staticmethod
    def sort_deps(dep_list):
        return sorted(dep_list, key=lambda x: len(x.deps), reverse=True)

    @staticmethod
    def parse_stored_deps_multiline(text: str) -> List:
        dep_list = []
        for line in [l.strip(' ') for l in text.split('\n')]:
            if not line:
                continue
            dep = TableDeps.parse_stored_deps_line(line)
            if dep:
                dep_list.append(dep)
        return dep_list

    @staticmethod
    def parse_stored_deps_line(line: str):
        if not line.startswith('pk:['):
            return None
        parts = line.split(', ')
        if len(parts) == 0:
            return None

        td = TableDeps(None)
        td.own_table_pk = parts[0][len('pk:'):].strip('[]').split(',')
        subparts = [p.split(' -> ') for p in parts[1:]]
        rec_lists = [(p[0].split('.'), p[1].split('.')) for p in subparts]
        dep_recs = [DependencyRecord(p[0][0], p[0][1], p[1][0], p[1][1]) for p in rec_lists]

        td.deps = dep_recs
        return td


