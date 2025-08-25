// cypress/support/commands.ts
// Custom commands for Fleet Tracker testing

// Login command
Cypress.Commands.add('login', (email?: string, password?: string) => {
  const finalEmail = email ?? 'test@fleettracker.com';
  const finalPassword = password ?? 'testpassword123';
  cy.visit('/login')
  cy.get('[data-testid="email-input"]').type(finalEmail)
  cy.get('[data-testid="password-input"]').type(finalPassword)
  cy.get('[data-testid="login-button"]').click()
  cy.url().should('not.include', '/login')
})

// Get element by test ID
Cypress.Commands.add('getByTestId', (testId: string) => {
  return cy.get(`[data-testid="${testId}"]`)
})

// Mock API responses for testing
export const mockApiResponses = () => {
  // Mock authentication
  cy.intercept('POST', '/api/auth/login', {
    statusCode: 200,
    body: {
      access_token: 'mock-jwt-token',
      user: {
        id: '1',
        email: 'test@fleettracker.com',
        name: 'Test User'
      }
    }
  }).as('login')

  // Mock vehicles
  cy.intercept('GET', '/api/vehicles', {
    statusCode: 200,
    body: [
      {
        id: '1',
        license_plate: 'TEST-001',
        make: 'Toyota',
        model: 'Camry',
        year: 2023,
        status: 'active'
      }
    ]
  }).as('getVehicles')

  // Mock locations
  cy.intercept('GET', '/api/locations/current', {
    statusCode: 200,
    body: [
      {
        vehicle_id: '1',
        latitude: 10.7769,
        longitude: 106.7009,
        speed: 45.5,
        timestamp: new Date().toISOString()
      }
    ]
  }).as('getCurrentLocations')

  // Mock analytics
  cy.intercept('GET', '/api/analytics', {
    statusCode: 200,
    body: {
      fleet_overview: {
        total_vehicles: 1,
        active_vehicles: 1,
        total_distance: 1250.5,
        avg_speed: 42.3
      },
      distance_analytics: {
        today: 125.5,
        week: 875.2,
        month: 3520.8
      }
    }
  }).as('getAnalytics')

  // Mock alerts
  cy.intercept('GET', '/api/alerts', {
    statusCode: 200,
    body: {
      alerts: [
        {
          id: '1',
          vehicle_id: '1',
          type: 'speed_limit',
          severity: 'high',
          message: 'Vehicle exceeding speed limit',
          status: 'active',
          timestamp: new Date().toISOString()
        }
      ]
    }
  }).as('getAlerts')
}
