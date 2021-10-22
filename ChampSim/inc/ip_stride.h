// Describes a single entry in the prefetch table

class IP_TRACKER {

  public:

  // the IP we're tracking
  uint64_t ip;

  // the last address accessed by this IP
  uint64_t last_cl_addr;

  // the stride between the last two addresses accessed by this IP
  int64_t last_stride;

  // use LRU to evict old IP trackers_l1d
  uint32_t lru;

  // no. of useful prefetches generated for this IP
  uint64_t pf_useful;

  // no. of useless prefetches generated for this IP
  uint64_t pf_useless;

  // degree fir current IP
  uint64_t degree;

  IP_TRACKER() {
    ip = 0;
    last_cl_addr = 0;
    last_stride = 0;
    lru = 0;
  };

};