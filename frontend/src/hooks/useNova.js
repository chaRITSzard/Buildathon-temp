import { useEffect, useState } from 'react'
import {
  askNova,
  decideNova,
  getActions,
} from '../api/novaApi'

export function useNova() {
  const [answer, setAnswer] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [decision, setDecision] = useState(null)
  const [decisionHistory, setDecisionHistory] = useState([])

  useEffect(() => {
    const loadHistory = async () => {
      try {
        const result = await getActions()

        setDecisionHistory(result.actions || [])
      } catch (error) {
        console.error(
          'Failed to load decision history:',
          error
        )
      }
    }

    loadHistory()
  }, [])

  const loadDecisionHistory = async () => {
    try {
      const result = await getActions()

      setDecisionHistory(result.actions || [])

      return result.actions || []
    } catch (error) {
      console.error(
        'Failed to load decision history:',
        error
      )

      return []
    }
  }

  const ask = async (question) => {
    setLoading(true)
    setError(null)
    setDecision(null)

    try {
      const result = await askNova(question)

      setAnswer(result)

      return result
    } catch (error) {
      setError(error.message)
      throw error
    } finally {
      setLoading(false)
    }
  }

  const decide = async (action) => {
    if (!answer) {
      return
    }

    setError(null)

    try {
      const result = await decideNova({
        question: answer.question,
        agent: answer.agent,
        action,
      })

      setDecision(result)

      await loadDecisionHistory()

      return result
    } catch (error) {
      setError(error.message)
    }
  }

  return {
    answer,
    loading,
    error,
    decision,
    decisionHistory,
    ask,
    decide,
    loadDecisionHistory,
  }
}