import { useQuery } from '@tanstack/react-query'
import { logsApi } from '../services/api'

export function useLogs(params = {}) {
  return useQuery({
    queryKey: ['logs', params],
    queryFn: () => logsApi.list(params),
    refetchInterval: 10000,
  })
}
