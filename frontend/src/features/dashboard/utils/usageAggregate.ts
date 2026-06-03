import { DeviceUsageLiveItem } from '../types/usageLive';
import { ServerNetworkThroughput } from '../types/networkThroughput';

/** Sum all VPN usage samples = total traffic through the server (all reporting peers). */
export function aggregateServerUsage(items: DeviceUsageLiveItem[]): ServerNetworkThroughput {
  return items.reduce(
    (acc, item) => ({
      rx_mib_per_sec: acc.rx_mib_per_sec + item.rx_mib_per_sec,
      tx_mib_per_sec: acc.tx_mib_per_sec + item.tx_mib_per_sec,
      total_mib_per_sec: acc.total_mib_per_sec + item.total_mib_per_sec,
      reporting_clients: acc.reporting_clients + 1,
    }),
    { rx_mib_per_sec: 0, tx_mib_per_sec: 0, total_mib_per_sec: 0, reporting_clients: 0 },
  );
}
