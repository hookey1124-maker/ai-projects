import type { DataCenterState, DataSourceKind } from './types';

export const selectCurrentPeriod = (state: DataCenterState) => state.currentPeriod;

export const selectPreviousPeriod = (state: DataCenterState) => state.previousPeriod;

export const selectVisiblePeriods = (state: DataCenterState) => state.visiblePeriods;

export const selectSourceStatus = (state: DataCenterState, source: DataSourceKind) => state.sources[source].status;

export const selectWarningsBySource = (state: DataCenterState, source: DataSourceKind) => state.sources[source].warnings;
