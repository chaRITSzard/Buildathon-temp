import Header from './components/header'
import QuestionBar from './components/QuestionBar'
import ResponsePanel from './components/ResponsePanel'
import ActionCard from './components/ActionCard'
import BoardroomScene from './scenes/BoardRoomScene'
import { useNova } from './hooks/useNova'
import DecisionHistory from './components/DecisionHistory'

import './App.css'

function App() {
  const nova = useNova()

  return (
    <main>
      <Header />

      <section className="boardroom-section">
        <BoardroomScene
          activeAgent={nova.answer?.agent}
        />
      </section>

      <QuestionBar
        onAsk={nova.ask}
        loading={nova.loading}
      />

      <ResponsePanel
        answer={nova.answer}
        loading={nova.loading}
        error={nova.error}
        onDecision={nova.decide}
        decision={nova.decision}
      />

      <DecisionHistory
        decisions={nova.decisionHistory}
      />

      {nova.pendingAction && (
        <ActionCard
          actionData={nova.pendingAction}
          onApprove={nova.approveAction}
          onReject={nova.rejectAction}
          loading={nova.actionLoading}
        />
      )}
    </main>
  )
}

export default App