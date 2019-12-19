function out = get_path(instrument_cycle, proposal, location, run)
    out = sprintf('/gpfs/exfel/exp/SQS/%06d/p%06d/%s/r%04d', instrument_cycle, proposal, location, run);
end