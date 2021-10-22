#include "block.h"

int PACKET_QUEUE::check_queue(PACKET *packet) {
  if ((head == tail) && occupancy == 0)
    return -1;

  if (head < tail) {
    for (uint32_t i = head; i < tail; i++) {
      if (NAME == "L1D_WQ") {
        if (entry[i].full_addr == packet->full_addr) {
          DP(if (warmup_complete[packet->cpu]) {
            cout << "[" << NAME << "] " << __func__ << " cpu: " << packet->cpu
                 << " instr_id: " << packet->instr_id
                 << " same address: " << hex << packet->address;
            cout << " full_addr: " << packet->full_addr << dec
                 << " by instr_id: " << entry[i].instr_id << " index: " << i;
            cout << " cycle " << packet->event_cycle << endl;
          });
          return i;
        }
      } else {
        if (entry[i].address == packet->address) {
          DP(if (warmup_complete[packet->cpu]) {
            cout << "[" << NAME << "] " << __func__ << " cpu: " << packet->cpu
                 << " instr_id: " << packet->instr_id
                 << " same address: " << hex << packet->address;
            cout << " full_addr: " << packet->full_addr << dec
                 << " by instr_id: " << entry[i].instr_id << " index: " << i;
            cout << " cycle " << packet->event_cycle << endl;
          });
          return i;
        }
      }
    }
  } else {
    for (uint32_t i = head; i < SIZE; i++) {
      if (NAME == "L1D_WQ") {
        if (entry[i].full_addr == packet->full_addr) {
          DP(if (warmup_complete[packet->cpu]) {
            cout << "[" << NAME << "] " << __func__ << " cpu: " << packet->cpu
                 << " instr_id: " << packet->instr_id
                 << " same address: " << hex << packet->address;
            cout << " full_addr: " << packet->full_addr << dec
                 << " by instr_id: " << entry[i].instr_id << " index: " << i;
            cout << " cycle " << packet->event_cycle << endl;
          });
          return i;
        }
      } else {
        if (entry[i].address == packet->address) {
          DP(if (warmup_complete[packet->cpu]) {
            cout << "[" << NAME << "] " << __func__ << " cpu: " << packet->cpu
                 << " instr_id: " << packet->instr_id
                 << " same address: " << hex << packet->address;
            cout << " full_addr: " << packet->full_addr << dec
                 << " by instr_id: " << entry[i].instr_id << " index: " << i;
            cout << " cycle " << packet->event_cycle << endl;
          });
          return i;
        }
      }
    }
    for (uint32_t i = 0; i < tail; i++) {
      if (NAME == "L1D_WQ") {
        if (entry[i].full_addr == packet->full_addr) {
          DP(if (warmup_complete[packet->cpu]) {
            cout << "[" << NAME << "] " << __func__ << " cpu: " << packet->cpu
                 << " instr_id: " << packet->instr_id
                 << " same address: " << hex << packet->address;
            cout << " full_addr: " << packet->full_addr << dec
                 << " by instr_id: " << entry[i].instr_id << " index: " << i;
            cout << " cycle " << packet->event_cycle << endl;
          });
          return i;
        }
      } else {
        if (entry[i].address == packet->address) {
          DP(if (warmup_complete[packet->cpu]) {
            cout << "[" << NAME << "] " << __func__ << " cpu: " << packet->cpu
                 << " instr_id: " << packet->instr_id
                 << " same address: " << hex << packet->address;
            cout << " full_addr: " << packet->full_addr << dec
                 << " by instr_id: " << entry[i].instr_id << " index: " << i;
            cout << " cycle " << packet->event_cycle << endl;
          });
          return i;
        }
      }
    }
  }

  return -1;
}

void PACKET_QUEUE::add_queue(PACKET *packet) {
#ifdef SANITY_CHECK
  if (occupancy && (head == tail))
    assert(0);
#endif

  // add entry
  entry[tail] = *packet;

  DP(if (warmup_complete[packet->cpu]) {
    cout << "[" << NAME << "] " << __func__ << " cpu: " << packet->cpu
         << " instr_id: " << packet->instr_id;
    cout << " address: " << hex << entry[tail].address
         << " full_addr: " << entry[tail].full_addr << dec;
    cout << " head: " << head << " tail: " << tail
         << " occupancy: " << occupancy
         << " event_cycle: " << entry[tail].event_cycle << endl;
  });

  occupancy++;
  tail++;
  if (tail >= SIZE)
    tail = 0;
}

void PACKET_QUEUE::remove_queue(PACKET *packet) {
#ifdef SANITY_CHECK
  if ((occupancy == 0) && (head == tail))
    assert(0);
#endif

  DP(if (warmup_complete[packet->cpu]) {
    cout << "[" << NAME << "] " << __func__ << " cpu: " << packet->cpu
         << " instr_id: " << packet->instr_id;
    cout << " address: " << hex << packet->address
         << " full_addr: " << packet->full_addr << dec
         << " fill_level: " << packet->fill_level;
    cout << " head: " << head << " tail: " << tail
         << " occupancy: " << occupancy
         << " event_cycle: " << packet->event_cycle << endl;
  });

  // reset entry
  PACKET empty_packet;
  *packet = empty_packet;

  occupancy--;
  head++;
  if (head >= SIZE)
    head = 0;
}

// -------------- MadCache ------------- //

/**
 * get_default_policy - Returns the current default policy
 */
POLICY PREDICTOR::get_default_policy()
{
  return static_cast<POLICY>((default_policy_counter >> 9) & 1);
}

/**
 * get_policy - Returns the policy to be used for this PC.
 * If a hit in the predictor, returns a PC-specific policy.
 * Otherwise returns the default policy.
 */
POLICY PREDICTOR::get_policy(uint64_t pc)
{
  POLICY default_policy = get_default_policy();
  for (int i = 0; i < 1024; i++) {
    if (pred_entries[i].pc == pc && default_policy == pred_entries[i].policy &&
     pred_entries[i].num_entries)
      return static_cast<POLICY>((pred_entries[i].counter >> 5)&1);
  }
  return default_policy;
}

/**
 * add_entry - Add an entry in the predictor for pc.
 * If an entry already exists, simply increments the corresponding
 * counter. Otherwise tries to find and initialize a fresh entry.
 * Returns the corresponding index if a merged or fresh entry is found/
 * created. Otherwise, returns -1 to indicate unavailability of slots.
 */
int PREDICTOR::add_entry(uint64_t pc)
{
  POLICY default_policy = get_default_policy();
  int free_index = -1;
  for (int i = 0; i < 1024; i++) {
    if (pred_entries[i].pc == pc && default_policy == pred_entries[i].policy &&
     pred_entries[i].num_entries) {
      // Simply increment num_entries and return this index
      pred_entries[i].num_entries++;
      return i;
    } else if (pred_entries[i].pc == (uint64_t)(-1))
      free_index = i;
  }

  if (free_index != -1) {
    // Unable to merge, but at least found a free slot
    pred_entries[free_index].policy = default_policy;
    pred_entries[free_index].pc = pc;
    pred_entries[free_index].counter = (1 << 5) - 1;
    pred_entries[free_index].num_entries = 1;
  }
  return free_index;
}

/**
 * update_hit - Called to indicate a hit in the LLC for a 
 * request to a cacheline that has an associated pred-index 
 * `index`. Decrements the counter of the corresponding entry, 
 * except if we are already at 0.
 */
void PREDICTOR::update_hit(int index)
{
  if (pred_entries[index].counter)
    pred_entries[index].counter--;
}

/**
 * update_evicted - Called to indicate that a cacheline with
 * associated pred-index `index` has been evicted. Decrements
 * the num_entries of the corresponding entry, and increments
 * its counter if reuse is not set.
 * Further, removes the entry in the predictor if the 
 * num_entries field falls to 0 for this pc.
 */
void PREDICTOR::update_evicted(int index, bool reuse)
{
  if (--pred_entries[index].num_entries == 0) {
    // No more users of this entry -- mark invalid
    pred_entries[index].pc = (uint64_t)(-1);
  } else if (!reuse) {
    // At least one other user, and no reuse
    // Increment counter, unless already at max
    if (pred_entries[index].counter != (1<<6)-1)
      pred_entries[index].counter++;
  }
}