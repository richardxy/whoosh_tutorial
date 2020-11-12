#!/usr/bin/env python
import sys
import os
import os.path
import glob
from whoosh import index
from whoosh import highlight
from whoosh.fields import ID, TEXT, Schema
from whoosh.reading import TermNotFound
from whoosh.qparser import QueryParser
from whoosh.analysis import StemmingAnalyzer



def get_or_create_index(index_dir,entries):
    if not os.path.exists(index_dir):
        os.mkdir(index_dir)

    if index.exists_in(index_dir):
        return index.open_dir(index_dir)
    else:
        return full_index(index_dir,entries)


def full_index(index_dir,entries):
    idx = index.create_in(index_dir, SCHEMA)
    writer = idx.writer()

    datas = []

    for ent in entries:    
        file = open(ent,mode='r')
        
        # read all lines at once    
        all_of_it = file.read()
        all_of_it = all_of_it.replace('\n',' ')
        data = {'title':ent.split('/')[1],'path':ent,'content':all_of_it}
        datas.append(data)

    # TODO: get data

    for data in datas:
        writer.add_document(**data)

    writer.commit()
    return idx


def search(user_query, index_dir,entries):
    # get index to search
    idx = get_or_create_index(index_dir,entries)

    # parse the user_query
    qp = QueryParser('content', schema=idx.schema)
    query = qp.parse(user_query)

    # get searcher
    with idx.searcher() as searcher:
        # do search
        try:
            results = searcher.search(query)
        except TermNotFound:
            results = []

        # print results
        print("{} files matched:".format(len(results)))
        # results.fragmenter.maxchars = 100
        for hit in results:
            # filecontents = ''
            # with open(hit['text_filename']) as file_:
            #     filecontents = file_.read()
            #     highlight = (hit
            #                  .highlights("content", text=filecontents, top=2)
            #                  .replace("\n", " ").strip())
            print("  * {}".format(hit['title']))


if __name__ == '__main__':
    SCHEMA = Schema(title=TEXT(stored=True),
                    content=TEXT(analyzer=StemmingAnalyzer()),
                    path=ID(stored=True))

    entries = glob.glob('text/*.text')

    try:
        query = sys.argv[1]
    except IndexError:
        print('you need to provide a query. assuming "chicken" query.')
        search('chicken', 'index_dir',entries)
    else:
        search(query, 'index_dir',entries)
