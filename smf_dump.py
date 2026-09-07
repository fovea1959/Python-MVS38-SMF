import logging
import sys
import utils

import SMF

def main(argv):
    import json
    records = utils.read_list_of_bytes("vb.json")
    smf_parser = SMF.SMFParser()
    for record in records:
        smf_record = smf_parser.make_smf_from_bytes(record, type_filter=(70, ))
        if smf_record is not None:
            logging.info("Got %s", smf_record)
            logging.info(" %s", json.dumps((smf_record.__class__.__name__, smf_record.clean_dict()), indent=1,default=str))
    logging.info("total records = %s", smf_parser.all_counter)
    logging.info("processed records = %s", smf_parser.filtered_counter)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main(sys.argv[1:])