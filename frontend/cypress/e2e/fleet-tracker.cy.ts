// End-to-End Test Configuration
// Cypress E2E Testing for Fleet Tracker

import { mockApiResponses } from '../support/commands'

describe('Fleet Tracker E2E Tests', () => {
  beforeEach(() => {
    // Setup API mocking
    mockApiResponses()
    
    // Visit application
    cy.visit('/')
  })

  describe('Authentication Flow', () => {
    it('should login successfully with valid credentials', () => {
      cy.login()
      
      cy.url().should('include', '/dashboard')
      cy.getByTestId('header').should('contain', 'Fleet Tracker')
    })

    it('should show error with invalid credentials', () => {
      cy.visit('/login')
      cy.getByTestId('email-input').type('invalid@email.com')
      cy.getByTestId('password-input').type('wrongpassword')
      
      // Mock failed login
      cy.intercept('POST', '/api/auth/login', {
        statusCode: 401,
        body: { message: 'Invalid credentials' }
      }).as('failedLogin')
      
      cy.getByTestId('login-button').click()
      cy.wait('@failedLogin')
      
      cy.getByTestId('error-message').should('be.visible')
    })

    it('should logout successfully', () => {
      // Login first
      cy.login()
      
      // Logout
      cy.getByTestId('logout-button').click()
      cy.url().should('include', '/login')
    })
  })

  describe('Dashboard', () => {
    beforeEach(() => {
      cy.login()
    })

    it('should display dashboard with key metrics', () => {
      cy.visit('/dashboard')
      
      cy.getByTestId('total-vehicles-card').should('be.visible')
      cy.getByTestId('active-vehicles-card').should('be.visible')
      cy.getByTestId('alerts-card').should('be.visible')
      cy.getByTestId('critical-alerts-card').should('be.visible')
    })

    it('should navigate between dashboard tabs', () => {
      cy.visit('/dashboard')
      
      cy.getByTestId('tab-overview').should('have.class', 'Mui-selected')
      
      cy.getByTestId('tab-vehicle-status').click()
      cy.getByTestId('vehicle-status-monitoring').should('be.visible')
      
      cy.getByTestId('tab-analytics').click()
      cy.getByTestId('analytics-dashboard').should('be.visible')
    })
  })

  describe('Vehicle Management', () => {
    beforeEach(() => {
      cy.login()
      cy.visit('/vehicles')
    })

    it('should display vehicle list', () => {
      cy.wait('@getVehicles')
      cy.getByTestId('vehicle-list').should('be.visible')
      cy.getByTestId('add-vehicle-button').should('be.visible')
    })

    it('should create a new vehicle', () => {
      // Mock create vehicle response
      cy.intercept('POST', '/api/vehicles', {
        statusCode: 201,
        body: {
          id: '2',
          license_plate: 'TEST-001',
          make: 'Toyota',
          model: 'Camry',
          year: 2023,
          status: 'active'
        }
      }).as('createVehicle')
      
      cy.getByTestId('add-vehicle-button').click()
      
      cy.getByTestId('vehicle-form').should('be.visible')
      cy.getByTestId('license-plate-input').type('TEST-001')
      cy.getByTestId('make-input').type('Toyota')
      cy.getByTestId('model-input').type('Camry')
      cy.getByTestId('year-input').type('2023')
      
      cy.getByTestId('save-vehicle-button').click()
      cy.wait('@createVehicle')
      
      cy.getByTestId('success-message').should('be.visible')
      cy.getByTestId('vehicle-list').should('contain', 'TEST-001')
    });

    it('should edit an existing vehicle', () => {
      // Assuming a vehicle exists
      cy.get('[data-testid="vehicle-row"]').first().within(() => {
        cy.get('[data-testid="edit-button"]').click();
      });
      
      cy.get('[data-testid="vehicle-form"]').should('be.visible');
      cy.get('[data-testid="make-input"]').clear().type('Honda');
      
      cy.get('[data-testid="save-vehicle-button"]').click();
      
      cy.get('[data-testid="success-message"]').should('be.visible');
    });

    it('should delete a vehicle', () => {
      cy.get('[data-testid="vehicle-row"]').first().within(() => {
        cy.get('[data-testid="delete-button"]').click();
      });
      
      cy.get('[data-testid="confirm-delete-button"]').click();
      
      cy.get('[data-testid="success-message"]').should('be.visible');
    });
  });

  describe('Live Map', () => {
    beforeEach(() => {
      cy.login('admin@fleettracker.com', 'password123');
      cy.visit('/map');
    });

    it('should display map with vehicle markers', () => {
      cy.get('[data-testid="map-container"]').should('be.visible');
      cy.get('.mapboxgl-canvas').should('be.visible');
      
      // Wait for map to load
      cy.wait(2000);
      
      cy.get('[data-testid="vehicle-marker"]').should('have.length.greaterThan', 0);
    });

    it('should show vehicle info on marker click', () => {
      cy.get('[data-testid="vehicle-marker"]').first().click();
      
      cy.get('[data-testid="vehicle-popup"]').should('be.visible');
      cy.get('[data-testid="vehicle-license-plate"]').should('be.visible');
      cy.get('[data-testid="vehicle-speed"]').should('be.visible');
    });

    it('should filter vehicles by status', () => {
      cy.get('[data-testid="status-filter"]').click();
      cy.get('[data-testid="filter-active"]').click();
      
      cy.get('[data-testid="vehicle-marker"]').should('have.length.greaterThan', 0);
    });
  });

  describe('Alert System', () => {
    beforeEach(() => {
      cy.login('admin@fleettracker.com', 'password123');
      cy.visit('/alerts');
    });

    it('should display alert dashboard', () => {
      cy.get('[data-testid="alert-dashboard"]').should('be.visible');
      cy.get('[data-testid="alert-stats"]').should('be.visible');
      cy.get('[data-testid="alert-list"]').should('be.visible');
    });

    it('should acknowledge an alert', () => {
      cy.get('[data-testid="alert-item"]').first().within(() => {
        cy.get('[data-testid="acknowledge-button"]').click();
      });
      
      cy.get('[data-testid="alert-item"]').first().should('contain', 'Đã xác nhận');
    });

    it('should filter alerts', () => {
      cy.get('[data-testid="filter-button"]').click();
      
      cy.get('[data-testid="filter-dialog"]').should('be.visible');
      cy.get('[data-testid="severity-filter"]').click();
      cy.get('[data-testid="severity-critical"]').click();
      
      cy.get('[data-testid="apply-filter-button"]').click();
      
      cy.get('[data-testid="alert-item"]').each(($el) => {
        cy.wrap($el).should('contain', 'critical');
      });
    });

    it('should manage alert rules', () => {
      cy.get('[data-testid="alert-rules-tab"]').click();
      
      cy.get('[data-testid="add-rule-button"]').click();
      
      cy.get('[data-testid="rule-form"]').should('be.visible');
      cy.get('[data-testid="rule-name-input"]').type('Test Speed Limit Rule');
      cy.get('[data-testid="rule-type-select"]').click();
      cy.get('[data-testid="rule-type-speed-limit"]').click();
      cy.get('[data-testid="speed-limit-input"]').type('80');
      
      cy.get('[data-testid="save-rule-button"]').click();
      
      cy.get('[data-testid="success-message"]').should('be.visible');
    });
  });

  describe('Analytics Dashboard', () => {
    beforeEach(() => {
      cy.login('admin@fleettracker.com', 'password123');
      cy.visit('/dashboard');
      cy.get('[data-testid="tab-analytics"]').click();
    });

    it('should display analytics metrics', () => {
      cy.get('[data-testid="analytics-dashboard"]').should('be.visible');
      cy.get('[data-testid="total-vehicles-metric"]').should('be.visible');
      cy.get('[data-testid="distance-metric"]').should('be.visible');
      cy.get('[data-testid="fuel-cost-metric"]').should('be.visible');
      cy.get('[data-testid="alerts-metric"]').should('be.visible');
    });

    it('should display charts', () => {
      cy.get('[data-testid="time-series-chart"]').should('be.visible');
      cy.get('[data-testid="fleet-status-chart"]').should('be.visible');
    });

    it('should change time series metric', () => {
      cy.get('[data-testid="metric-selector"]').click();
      cy.get('[data-testid="metric-fuel"]').click();
      
      // Chart should update
      cy.get('[data-testid="time-series-chart"]').should('be.visible');
    });

    it('should generate reports', () => {
      cy.get('[data-testid="fleet-summary-report"]').click();
      
      // Should trigger download
      cy.readFile('cypress/downloads/fleet_summary_report.pdf').should('exist');
    });
  });

  describe('Real-time Features', () => {
    beforeEach(() => {
      cy.login('admin@fleettracker.com', 'password123');
    });

    it('should receive real-time vehicle updates', () => {
      cy.visit('/map');
      
      // Simulate vehicle position update
      cy.task('sendVehicleUpdate', {
        vehicle_id: 'vh-001',
        latitude: 10.7769,
        longitude: 106.7009,
        speed: 45
      });
      
      // Should see updated position on map
      cy.get('[data-testid="vehicle-marker"]').first().should('be.visible');
    });

    it('should receive real-time alerts', () => {
      cy.visit('/dashboard');
      
      // Simulate new alert
      cy.task('sendAlert', {
        type: 'speed_limit',
        severity: 'high',
        vehicle_id: 'vh-001',
        message: 'Vehicle exceeded speed limit'
      });
      
      // Should see new alert in dashboard
      cy.get('[data-testid="recent-alerts"]').should('contain', 'exceeded speed limit');
    });
  });

  describe('Responsive Design', () => {
    beforeEach(() => {
      cy.login('admin@fleettracker.com', 'password123');
    });

    it('should work on mobile devices', () => {
      cy.viewport('iphone-6');
      
      cy.visit('/dashboard');
      cy.get('[data-testid="mobile-menu"]').should('be.visible');
      
      cy.visit('/vehicles');
      cy.get('[data-testid="vehicle-list"]').should('be.visible');
      
      cy.visit('/map');
      cy.get('[data-testid="map-container"]').should('be.visible');
    });

    it('should work on tablet devices', () => {
      cy.viewport('ipad-2');
      
      cy.visit('/dashboard');
      cy.get('[data-testid="dashboard-grid"]').should('be.visible');
    });
  });

  describe('Performance', () => {
    it('should load dashboard within acceptable time', () => {
      cy.login('admin@fleettracker.com', 'password123');
      
      const start = Date.now();
      cy.visit('/dashboard');
      cy.get('[data-testid="dashboard-loaded"]').should('be.visible').then(() => {
        const loadTime = Date.now() - start;
        expect(loadTime).to.be.lessThan(3000); // 3 seconds
      });
    });

    it('should handle large vehicle lists efficiently', () => {
      cy.task('createManyVehicles', 100);
      
      cy.login('admin@fleettracker.com', 'password123');
      cy.visit('/vehicles');
      
      cy.get('[data-testid="vehicle-list"]').should('be.visible');
      cy.get('[data-testid="vehicle-row"]').should('have.length', 10); // Pagination
    });
  });
});

// Custom Cypress Commands
declare global {
  namespace Cypress {
    interface Chainable {
      login(email?: string, password?: string): Chainable<void>;
    }
  }
}

Cypress.Commands.add('login', (email?: string, password?: string) => {
  cy.visit('/login');
  if (email) {
    cy.get('[data-testid="email-input"]').type(email);
  }
  if (password) {
    cy.get('[data-testid="password-input"]').type(password);
  }
  cy.get('[data-testid="login-button"]').click();
  cy.url().should('include', '/dashboard');
});
