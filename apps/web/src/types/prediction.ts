export interface PredictionRequest {
  text: string
}

export interface PredictionResponse {
  prediction: string
  confidence: number
}

export interface PredictionHistoryItem extends PredictionResponse {
  id: string
  text: string
  createdAt: string
}
