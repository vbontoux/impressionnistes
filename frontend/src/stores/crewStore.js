/**
 * Crew Member Store
 * Manages crew member state using Pinia
 */
import { defineStore } from 'pinia';
import * as crewService from '../services/crewService';
import { getErrorMessage } from '../services/apiClient';

export const useCrewStore = defineStore('crew', {
  state: () => ({
    crewMembers: [],
    loading: false,
    error: null,
  }),

  getters: {
    /**
     * Get crew members sorted by last name
     */
    sortedCrewMembers: (state) => {
      return [...state.crewMembers].sort((a, b) => 
        a.last_name.localeCompare(b.last_name)
      );
    },

    /**
     * Get assigned crew members (those assigned to a boat)
     */
    assignedCrewMembers: (state) => {
      return state.crewMembers.filter(member => member.assigned_boat_id);
    },

    /**
     * Get unassigned crew members
     */
    unassignedCrewMembers: (state) => {
      return state.crewMembers.filter(member => !member.assigned_boat_id);
    },

    /**
     * Get crew members with flagged issues
     */
    flaggedCrewMembers: (state) => {
      return state.crewMembers.filter(
        member => member.flagged_issues && member.flagged_issues.length > 0
      );
    },

    /**
     * Get RCPM members
     */
    rcpmMembers: (state) => {
      return state.crewMembers.filter(member => member.is_rcpm_member);
    },

    /**
     * Get external club members
     */
    externalMembers: (state) => {
      return state.crewMembers.filter(member => !member.is_rcpm_member);
    },

    /**
     * Get crew member by ID
     */
    getCrewMemberById: (state) => (id) => {
      return state.crewMembers.find(member => member.crew_member_id === id);
    },
  },

  actions:
{
    /**
     * Fetch all crew members from API
     */
    async fetchCrewMembers() {
      this.loading = true;
      this.error = null;
      
      try {
        this.crewMembers = await crewService.listCrewMembers();
      } catch (error) {
        this.error = getErrorMessage(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Create a new crew member
     */
    async createCrewMember(crewMemberData) {
      this.loading = true;
      this.error = null;
      
      try {
        const newMember = await crewService.createCrewMember(crewMemberData);
        this.crewMembers.push(newMember);
        return newMember;
      } catch (error) {
        this.error = getErrorMessage(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Update an existing crew member
     */
    async updateCrewMember(crewMemberId, updates) {
      this.loading = true;
      this.error = null;
      
      try {
        const updatedMember = await crewService.updateCrewMember(crewMemberId, updates);
        
        // Update in local state
        const index = this.crewMembers.findIndex(
          member => member.crew_member_id === crewMemberId
        );
        if (index !== -1) {
          this.crewMembers[index] = updatedMember;
        }
        
        return updatedMember;
      } catch (error) {
        this.error = getErrorMessage(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Delete a crew member
     */
    async deleteCrewMember(crewMemberId) {
      this.loading = true;
      this.error = null;
      
      try {
        await crewService.deleteCrewMember(crewMemberId);
        
        // Remove from local state
        this.crewMembers = this.crewMembers.filter(
          member => member.crew_member_id !== crewMemberId
        );
      } catch (error) {
        this.error = getErrorMessage(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Clear error state
     */
    clearError() {
      this.error = null;
    },
  },
});
