import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { messagesApi } from '../services/api'

export function useMessages(params = {}) {
  return useQuery({
    queryKey: ['messages', params],
    queryFn: () => messagesApi.list(params),
    refetchInterval: 30000,
  })
}

export function useDashboard() {
  return useQuery({
    queryKey: ['dashboard'],
    queryFn: messagesApi.dashboard,
    refetchInterval: 15000,
  })
}

export function useMessage(id) {
  return useQuery({
    queryKey: ['message', id],
    queryFn: () => messagesApi.get(id),
    enabled: !!id,
  })
}

export function useApproveMessage() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, approved, reason }) => messagesApi.approve(id, approved, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['messages'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    },
  })
}
