import logging
import sys
import utils

import SMF

def main(argv):
    import json
    records = utils.read_list_of_bytes("vb.json")
    smf_parser = SMF.SMFParser()
    type_filter = (242, )     # # None # (10, )   #None   # (4, )   # (70, 74)
    for record in records:
        smf_record = smf_parser.make_smf_from_bytes(record, type_filter=type_filter)
        if smf_record is not None:
            logging.info("Got %s", smf_record)
            logging.info(" %s", json.dumps((smf_record.__class__.__name__, smf_record.clean_dict()), indent=1,default=str))
    logging.info("total records = %s", smf_parser.all_counter)
    if type_filter is not None:
        logging.info("processed records = %s", smf_parser.filtered_counter)
        logging.info("all types = %d/%d", smf_parser.filtered_count, smf_parser.all_count)
    else:
        logging.info("all types = %d", smf_parser.all_count)
    logging.info("unimplemented smf parsers = %s", smf_parser.unimplemented_counter)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main(sys.argv[1:])