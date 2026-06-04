declare module '@svg-maps/world' {
  import type { Map } from 'svg-maps__common';

  const worldMap: Map;
  export default worldMap;
}

declare module 'svg-maps__common' {
  export interface MapLocation {
    name: string;
    id: string;
    path: string;
  }

  export interface Map {
    label: string;
    viewBox: string;
    locations: MapLocation[];
  }
}
